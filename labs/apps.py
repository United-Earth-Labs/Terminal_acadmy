"""Labs app configuration."""
from django.apps import AppConfig


class LabsConfig(AppConfig):
    """Configuration for the labs app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'labs'
    verbose_name = 'Terminal Labs'
