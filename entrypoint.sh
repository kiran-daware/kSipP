#!/bin/sh

set -e  # Exit on error

echo "Running migrations..."
python manage.py migrate --noinput

echo "Loading initial data if needed..."
python manage.py load_initial_if_empty

# Start Nginx in the background
nginx -g 'daemon on;'

# Start Uvicorn in the foreground
# Adjust host and port as needed; no Unix socket by default
exec uvicorn easySIPp_project.asgi:application \
    --host 127.0.0.1 \
    --port 8000 \
    --workers 3 \
    --proxy-headers \
    --forwarded-allow-ips="*"
