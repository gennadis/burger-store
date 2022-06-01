#!/bin/bash
set -e

echo 'Pulling code updates from GitHub...'
git pull

echo 'Installing project requirements...'
source venv/bin/activate
pip install -r requirements.txt
npm ci --dev

echo 'Building frontend...'
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

echo 'Collecting static files...'
python manage.py collectstatic

echo 'Applying migrations...'
python manage.py migrate

echo 'Reloading systemd daemons'
sudo systemctl reload nginx
sudo systemctl restart burger-store.service

echo 'Deploy completed'
