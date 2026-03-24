"""Progress app configuration."""
from django.apps import AppConfig


class ProgressConfig(AppConfig):
    """Configuration for the progress app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'progress'
    verbose_name = 'Progress & Achievements'
