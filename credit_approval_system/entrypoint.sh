#!/bin/sh
if [ -n "$DATABASE_HOST" ]; then
  echo "Waiting for Postgres..."
  while ! nc -z $DATABASE_HOST $DATABASE_PORT; do
    sleep 1
  done
fi

python manage.py migrate --noinput

exec "$@"
