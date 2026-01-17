"""
User-related signals for Terminal Academy.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile_data(sender, instance, created, **kwargs):
    """Create initial user data when a new user is created."""
    if created:
        # Initialize any default user-related data here
        # For example, creating a UserXP record
        from progress.models import UserXP
        UserXP.objects.get_or_create(user=instance)
