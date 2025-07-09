#!/usr/bin/env sh
python manage.py migrate --noinput
exec python manage.py runserver 0.0.0.0:5005
