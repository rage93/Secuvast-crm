#!/usr/bin/env sh 
# exit on error
set -o errexit

# Install & Execute WebPack 
yarn 
yarn build

# Install modules 
python -m pip install --upgrade pip
pip install -r requirements.txt

# Collect Static
python manage.py collectstatic --no-input

# Migrate DB
python manage.py makemigrations
python manage.py migrate
