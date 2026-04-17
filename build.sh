#!/bin/bash
set -e

export DJANGO_SETTINGS_MODULE=core.settings.vercel
export DEBUG=False

echo "Building Terminal Academy for Vercel..."
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "Build complete!"
