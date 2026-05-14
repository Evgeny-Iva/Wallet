#!/bin/sh
echo "DATABASE_URL is: $DATABASE_URL"
echo "Waiting for PostgreSQL to be ready..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL is ready. Running migrations..."

alembic upgrade head

echo "Starting application..."
exec uvicorn api.main:app --host 0.0.0.0 --port 8000