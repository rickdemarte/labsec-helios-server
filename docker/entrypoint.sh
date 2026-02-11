#!/usr/bin/env sh
set -eu

# Wait for Postgres (best-effort)
if [ -n "${DATABASE_URL:-}" ]; then
  echo "Waiting for database..."
  for i in $(seq 1 60); do
    if uv run python -c "import os, urllib.parse, psycopg2; u=urllib.parse.urlparse(os.environ['DATABASE_URL']); psycopg2.connect(host=u.hostname, port=u.port or 5432, user=u.username, password=u.password, dbname=(u.path or '/')[1:]).close()" 2>/dev/null; then
      break
    fi
    sleep 1
  done
fi

# Run migrations
uv run python manage.py migrate --noinput

# Optional: background celery worker (needs RabbitMQ)
if [ "${START_CELERY:-1}" = "1" ]; then
  echo "Starting celery worker (background)..."
  uv run celery -A helios worker -l INFO &
fi

# Run web server
if [ "${DJANGO_DEBUG_SERVER:-1}" = "1" ]; then
  exec uv run python manage.py runserver 0.0.0.0:8000
else
  exec uv run gunicorn wsgi:application --bind 0.0.0.0:8000 --workers ${GUNICORN_WORKERS:-2} --threads ${GUNICORN_THREADS:-4}
fi
