#!/bin/bash
set -e

echo "Building Terminal Academy for Vercel..."

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Don't run migrations during build - they need a live database
# Instead, we'll collect static files only
echo "Collecting static files..."
python3 manage.py collectstatic --noinput --clear

echo "Build complete!"
echo ""
echo "Note: Run migrations manually after deployment with:"
echo "  vercel --prod"
echo ""
echo "Or connect to your database and run:"
echo "  python manage.py migrate"
