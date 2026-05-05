#!/bin/bash
set -e

if [ "$ENV" = 'DEV' ]; then
   echo "Running Development Server" # Запуск сервера для разработки
   exec python "identidock.py"
elif [ "$ENV" = 'UNIT' ]; then
   echo "Running Unit Tests"
   exec python "tests.py"
else
   echo "Running Production Server" # Запуск сервера для эксплуатации
   exec uwsgi --ini /app/uwsgi.ini
fi
