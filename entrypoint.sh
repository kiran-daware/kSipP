#!/bin/sh

set -e  # Exit on error

# Ensure the socket file doesn't exist from previous runs
SOCKFILE=/app/gunicorn.sock
[ -e "$SOCKFILE" ] && rm "$SOCKFILE"

# Start Nginx in the background
nginx -g 'daemon on;'

# Start Gunicorn in the foreground bound to the Unix socket
exec gunicorn EasySipP.wsgi:application \
    --bind unix:$SOCKFILE \
    --workers 3 \
    --access-logfile - \
    --error-logfile -
