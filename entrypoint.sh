#!/bin/sh

# Start Nginx in the background
nginx -g 'daemon on;'

# Start Gunicorn in the foreground (use --daemon for background)
# gunicorn EasySipP.wsgi --bind 0.0.0.0:8000 --daemon
gunicorn EasySipP.wsgi --bind unix:/app/gunicorn.sock

