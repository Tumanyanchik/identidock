from flask import Flask, Response, request, render_template
from flask_login import login_required, current_user
import hashlib
import html
import os
import logging
import requests
import redis

from extensions import db, login_manager, migrate, csrf
from models import User
from auth import auth_bp


def create_app():
    app = Flask(__name__)

    secret = os.environ.get('SECRET_KEY')
    env = os.environ.get('ENV', 'DEV')
    if not secret:
        if env == 'PROD':
            raise RuntimeError('SECRET_KEY обязателен при ENV=PROD')
        secret = 'dev-fallback-key'
        logging.warning('SECRET_KEY не задан — использую небезопасный fallback')
   
    app.config['SECRET_KEY'] = secret
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Войдите, чтобы продолжить'
    login_manager.login_message_category = 'warning'

    app.register_blueprint(auth_bp)
    return app

app = create_app()

redis_host = os.getenv('REDIS_HOST', 'redis')
cache = redis.StrictRedis(host=redis_host, port=6379, db=0)
salt = "UNIQUE_SALT"
default_name = 'Tumanyan Artem'
debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, log_level, logging.INFO))
logger = logging.getLogger(__name__)


@app.route('/', methods=['GET', 'POST'])
def mainpage():
   name = default_name

   if request.method == 'POST':
      name = html.escape(request.form['name'], quote=True)

   salted_name = salt + name
   name_hash = hashlib.sha256(salted_name.encode()).hexdigest()

   return render_template('index.html', name=name, name_hash=name_hash)
   

@app.route('/monster/<name>')
def get_identicon(name):
   name = html.escape(name, quote=True)
   image = cache.get(name)
   if image:
      logger.info("From cache")
   else:
      logger.info("Cache miss")
      r = requests.get('http://dnmonster:8080/monster/' + name + '?size=360')
      image = r.content
      cache.set(name, image, ex=3600)
   return Response(image, mimetype='image/png')

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html')

if __name__=='__main__':
   app.run(debug=debug_mode, host='0.0.0.0')
   
