"""
Vercel WSGI entry point for Terminal Academy.
"""
import os
import sys

# Set environment variables for Vercel
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.vercel')

# Import Django WSGI handler
from django.core.wsgi import get_wsgi_application

# Create the WSGI application
application = get_wsgi_application()

# Vercel expects 'app' variable
app = application
