"""
Production settings for PythonAnywhere deployment.
"""
from .base import *

# Security
DEBUG = False
SECRET_KEY = config('SECRET_KEY')  # Required in production

# Hosts
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# HTTPS settings (PythonAnywhere provides HTTPS)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Logging - write to file on PythonAnywhere
LOGGING['handlers']['file'] = {
    'level': 'WARNING',
    'class': 'logging.FileHandler',
    'filename': BASE_DIR / 'logs' / 'django.log',
    'formatter': 'verbose',
}

LOGGING['loggers']['django']['handlers'] = ['console', 'file']

# Sentry (optional - for error tracking)
SENTRY_DSN = config('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=True
    )
