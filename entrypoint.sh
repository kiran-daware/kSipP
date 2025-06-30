#!/bin/sh

set -e  # Exit on error

echo "Running migrations..."
python manage.py migrate --noinput

# Start Nginx in the background
nginx -g 'daemon on;'

# Start Uvicorn in the foreground
# Adjust host and port as needed; no Unix socket by default
exec uvicorn EasySipP.asgi:application \
    --host 127.0.0.1 \
    --port 8000 \
    --workers 3 \
    --proxy-headers \
    --forwarded-allow-ips="*"
