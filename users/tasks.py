"""
Celery tasks for user management.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def cleanup_expired_sessions():
    """Remove expired user sessions."""
    from .models import UserSession
    
    # Delete sessions inactive for more than 30 days
    cutoff = timezone.now() - timedelta(days=30)
    deleted, _ = UserSession.objects.filter(
        last_activity__lt=cutoff
    ).delete()
    
    return f'Deleted {deleted} expired sessions.'


@shared_task
def unlock_expired_accounts():
    """Unlock accounts that have passed their lock duration."""
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    unlocked = User.objects.filter(
        account_locked_until__lt=timezone.now()
    ).update(
        account_locked_until=None,
        failed_login_attempts=0
    )
    
    return f'Unlocked {unlocked} accounts.'


@shared_task
def send_email_verification(user_id):
    """Send email verification to a user."""
    from django.contrib.auth import get_user_model
    from django.core.mail import send_mail
    from django.conf import settings
    
    User = get_user_model()
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return 'User not found.'
    
    # Generate verification token
    from .auth import generate_jwt_token
    token = generate_jwt_token(user, token_type='email_verification')
    
    # Send email
    verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    send_mail(
        subject='Verify your Terminal Academy email',
        message=f'Click here to verify your email: {verification_url}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
    
    return f'Verification email sent to {user.email}.'
