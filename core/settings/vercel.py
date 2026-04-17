"""
Vercel serverless deployment settings for Terminal Academy.
Uses external PostgreSQL (Neon/Supabase) instead of SQLite.
"""
from .base import *
import os

# Security
DEBUG = config('DEBUG', default=False, cast=bool)
SECRET_KEY = config('SECRET_KEY', default='django-insecure-vercel-key-change-in-production')

# Hosts - Vercel provides dynamic URLs
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS',
    default='*.vercel.app,localhost,127.0.0.1',
    cast=Csv()
)

# Add current host dynamically (for preview deployments)
import socket
ALLOWED_HOSTS.append(socket.gethostname())

# Disable HTTPS-only cookies for serverless (Vercel handles HTTPS at edge)
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False

# Database - Use external PostgreSQL (Neon, Supabase, etc.)
# Format: postgres://user:password@host:port/database
DATABASES = {
    'default': dj_database_url.config(
        default='sqlite:///' + str(BASE_DIR / 'db.sqlite3'),  # Fallback for local dev
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Override with external DB if provided
DATABASE_URL = config('DATABASE_URL', default='')
if DATABASE_URL:
    DATABASES['default'] = dj_database_url.parse(DATABASE_URL, conn_max_age=600)

# Static files - WhiteNoise for serverless
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static'] if os.path.exists(BASE_DIR / 'static') else []
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files - Use external storage for production (Cloudinary, AWS S3, etc.)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Use default file storage for serverless (can be replaced with S3/Cloudinary)
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

# Cache - Use dummy cache for serverless (avoids needing cache table in DB)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Sessions - Database backed
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Logging - Console only for serverless (no file system)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'axes': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    },
}

# CORS - Allow all origins for API access
CORS_ALLOWED_ORIGINS = config(
    'CORS_ALLOWED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=Csv()
)

# CSRF trusted origins
CSRF_TRUSTED_ORIGINS = config(
    'CSRF_TRUSTED_ORIGINS',
    default='http://localhost:3000,http://127.0.0.1:3000',
    cast=Csv()
)

# Axes settings adjusted for serverless
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = timedelta(minutes=30)
AXES_RESET_ON_SUCCESS = True
AXES_FAILURE_LOG_FORMAT = (
    'AXES: Failed login attempt by {username} from {ip_address} '
    'via {user_agent} at {path_info}'
)

# Email - Console backend for serverless
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
