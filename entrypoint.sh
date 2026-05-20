#!/bin/sh
set -e

while ! nc -z db 5432; do
  echo 'Waiting for postgres...'
  sleep 1
done

echo 'Postgres is up!'
alembic upgrade head
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload