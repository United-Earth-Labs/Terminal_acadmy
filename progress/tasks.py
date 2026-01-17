"""
Celery tasks for progress management.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def aggregate_daily_analytics():
    """Aggregate daily analytics data."""
    from .models import UserProgress, UserXP
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Get stats for the day
    today = timezone.now().date()
    
    total_users = User.objects.count()
    active_users = User.objects.filter(last_login__date=today).count()
    
    # Log analytics (in production, send to analytics service)
    return {
        'date': str(today),
        'total_users': total_users,
        'active_users': active_users,
    }


@shared_task
def reset_expired_streaks():
    """Reset streaks for users who missed a day."""
    from .models import Streak
    from datetime import date
    
    yesterday = date.today() - timedelta(days=1)
    
    # Users whose last activity was before yesterday have broken their streak
    broken_streaks = Streak.objects.filter(
        last_activity_date__lt=yesterday,
        current_streak__gt=0
    )
    
    count = broken_streaks.update(current_streak=0)
    
    return f'Reset {count} expired streaks.'
