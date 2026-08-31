from flask import Flask, Response, request
import requests
import hashlib
import redis
import html
import os
import logging


app = Flask(__name__)
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

   header = '<html><head><title>Identidock</title></head><body>'
   body = '''<form method="POST">
             Hello <input type="text" name="name" value="{0}">
             <input type="submit" value="submit">
             </form>
             <p>You look like a:
             <img src="/monster/{1}"/>
             '''.format(name, name_hash)
   footer = '</body></html>' 
   
   return header + body + footer


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

if __name__=='__main__':
   app.run(debug=debug_mode, host='0.0.0.0')
   
