"""
Custom authentication backend for Terminal Academy.
"""
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Authenticate using email address instead of username.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """Authenticate a user by email and password."""
        email = kwargs.get('email', username)
        
        if email is None or password is None:
            return None
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Run the default password hasher once to reduce timing attacks
            User().set_password(password)
            return None
        
        # Check if account is locked
        if user.is_account_locked:
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def get_user(self, user_id):
        """Get a user by their ID."""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
