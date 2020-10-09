#!/bin/sh

printf "Running migrations..."
python -c 'import models.user as user;user.create_table()'
python -c 'import models.chat_history as ch;ch.create_table()'

printf "Starting webserver..."
gunicorn \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:80 \
  server:app
