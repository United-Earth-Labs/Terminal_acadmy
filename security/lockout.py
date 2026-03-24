"""
Security lockout response for django-axes.
"""
from django.http import JsonResponse


def lockout_response(request, credentials, *args, **kwargs):
    """
    Custom lockout response when user is blocked by django-axes.
    """
    return JsonResponse({
        'error': 'Too many failed login attempts. Please try again in 30 minutes.',
        'locked': True,
    }, status=403)
