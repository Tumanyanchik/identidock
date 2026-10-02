import unittest

import identidock
from extensions import db
from models import User


TEST_USERNAME = 'testuser'
TEST_EMAIL    = 'testuser@example.com'
TEST_PASSWORD = 'testpass'


class IdentidockTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        identidock.app.config['TESTING'] = True
        identidock.app.config['WTF_CSRF_ENABLED'] = False
        cls.client = identidock.app.test_client()

        # ENV=UNIT → entrypoint пропускает миграции (см. entrypoint.sh),
        # поэтому схему для тестов создаём сами. Если DEV-контейнер уже
        # накатил миграции, create_all() — no-op.
        with identidock.app.app_context():
            db.create_all()
            db.session.query(User).filter(User.username == TEST_USERNAME).delete()
            db.session.commit()

            user = User(username=TEST_USERNAME, email=TEST_EMAIL)
            user.set_password(TEST_PASSWORD)
            db.session.add(user)
            db.session.commit()
            cls.user_id = user.id

    @classmethod
    def tearDownClass(cls):
        with identidock.app.app_context():
            db.session.query(User).filter(User.username == TEST_USERNAME).delete()
            db.session.commit()
            db.session.remove()

    # ---------- helpers ----------

    def login(self):
        with self.client.session_transaction() as sess:
            sess['_user_id'] = str(self.user_id)
            sess['_fresh'] = True

    def logout(self):
        with self.client.session_transaction() as sess:
            sess.pop('_user_id', None)
            sess.pop('_fresh', None)

    # ---------- главная ----------

    def test_mainpage_get(self):
        assert self.client.get('/').status_code == 200

    def test_mainpage_post_uses_name(self):
        resp = self.client.post('/', data=dict(name='Moby Dick'))
        assert resp.status_code == 200
        assert 'Moby Dick' in resp.data.decode()

    def test_html_escaping(self):
        resp = self.client.post('/', data=dict(name='"><b>TEST</b><!--'))
        assert resp.status_code == 200
        assert b'<b>' not in resp.data

    def test_mainpage_hides_form_for_anonymous(self):
        self.logout()
        resp = self.client.get('/')
        body = resp.data.decode()
        assert 'name="name"' not in body          # поля формы нет
        assert '/monster/' not in body            # тега img с монстриком нет
        assert 'auth/login' in body               # зато есть ссылка на логин

    def test_mainpage_shows_form_when_logged_in(self):
        self.login()
        body = self.client.get('/').data.decode()
        assert 'name="name"' in body
        assert '/monster/' in body

    # ---------- монстрик ----------

    def test_monster_requires_login(self):
        self.logout()
        resp = self.client.get('/monster/bla')
        assert resp.status_code == 302
        assert '/login' in resp.headers['Location']

    def test_monster_returns_png_when_logged_in(self):
        self.login()
        resp = self.client.get('/monster/bla')
        assert resp.status_code == 200
        assert resp.mimetype == 'image/png'
        assert resp.data[:8] == b'\x89PNG\r\n\x1a\n'

    # ---------- профиль ----------

    def test_profile_requires_login(self):
        self.logout()
        resp = self.client.get('/profile')
        assert resp.status_code == 302
        assert '/login' in resp.headers['Location']

    def test_profile_shows_current_user(self):
        self.login()
        resp = self.client.get('/profile')
        assert resp.status_code == 200
        assert TEST_USERNAME in resp.data.decode()

    # ---------- healthz ----------

    def test_healthz_is_public(self):
        self.logout()
        resp = self.client.get('/healthz')
        assert resp.status_code == 200
        assert resp.get_json() == {'status': 'ok'}


if __name__ == '__main__':
    unittest.main()
