#!/usr/bin/env bash
python manage.py migrate --noinput
exec python manage.py runserver 0.0.0.0:5005
