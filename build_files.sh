#!/bin/bash

echo "Installing dependencies"

python -m pip install -r requirements.txt

echo "Building Tailwind"

python manage.py tailwind build

echo "Collecting static files"

python manage.py collectstatic --noinput

echo "Running migrations"

python manage.py migrate

python manage.py tailwind install --no-input
python manage.py tailwind build