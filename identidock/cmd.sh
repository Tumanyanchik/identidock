#!/bin/bash
set -e

if [ "$ENV" = 'DEV' ]; then
   echo "Running Development Server" # Запуск сервера для разработки
   export FLASK_DEBUG=True
   exec python "identidock.py"
elif [ "$ENV" = 'UNIT' ]; then
   echo "Running Unit Tests"
   export FLASK_DEBUG=True
   exec python "tests.py"
else
   echo "Running Production Server" # Запуск сервера для эксплуатации
   exec uwsgi --ini /app/uwsgi.ini
fi
