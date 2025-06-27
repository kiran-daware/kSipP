#!/bin/sh

set -e  # Exit on error

# Ensure the socket file doesn't exist from previous runs
SOCKFILE=/app/gunicorn.sock
[ -e "$SOCKFILE" ] && rm "$SOCKFILE"

# Start Nginx in the background
nginx -g 'daemon on;'

# Start Gunicorn in the foreground bound to the Unix socket
# Can increase workers to 3 after fixing config.ini issue
exec gunicorn EasySipP.wsgi:application \
    --bind unix:$SOCKFILE \
    --workers 1 \
    --access-logfile - \
    --error-logfile -
