#!/bin/bash
set -e

echo '1. Pulling code updates from GitHub...'
git pull

echo '2. Installing project requirements...'
source venv/bin/activate
pip install -r requirements.txt
npm ci --dev

echo '3. Building frontend...'
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

echo '4. Collecting static files...'
python manage.py collectstatic --noinput

echo '5. Applying migrations...'
python manage.py migrate

echo '6. Reloading systemd daemons...'
sudo systemctl reload nginx
sudo systemctl restart burger-store.service

echo '7. Deploy completed!'
