"""
Development settings.
"""
from .base import *

# Debug mode
DEBUG = True

# Allow all hosts in development
ALLOWED_HOSTS = ['*']

# Use SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# LocMem cache for development (faster than database)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

# Email to console
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Debug toolbar
INSTALLED_APPS += ['debug_toolbar', 'django_extensions']
MIDDLEWARE.insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')

INTERNAL_IPS = ['127.0.0.1']

# Disable security in development
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Simpler password for dev
AUTH_PASSWORD_VALIDATORS = []

# Disable axes in development (optional)
# AXES_ENABLED = False

# Logging
LOGGING['loggers']['django']['level'] = 'DEBUG'
