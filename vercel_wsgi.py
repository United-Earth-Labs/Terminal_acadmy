"""
Vercel WSGI entry point for Terminal Academy.
This handles the serverless environment properly.
"""
import os
import sys

# Add the project to path
sys.path.insert(0, os.path.dirname(__file__))

# Set environment variables for Vercel
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings.vercel')

# Import Django WSGI handler
from django.core.wsgi import get_wsgi_application

# Create the WSGI application
application = get_wsgi_application()

# Vercel expects 'app' variable
app = application
