"""
Celery tasks for security management.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta


@shared_task
def cleanup_old_audit_logs():
    """Clean up audit logs older than 90 days."""
    from .models import AuditLog
    
    cutoff = timezone.now() - timedelta(days=90)
    deleted, _ = AuditLog.objects.filter(created_at__lt=cutoff).delete()
    
    return f'Deleted {deleted} old audit logs.'


@shared_task
def cleanup_expired_blocks():
    """Remove expired IP blocks."""
    from .models import BlockedIP
    
    deleted, _ = BlockedIP.objects.filter(
        blocked_until__lt=timezone.now()
    ).delete()
    
    return f'Removed {deleted} expired IP blocks.'


@shared_task
def detect_brute_force_attacks():
    """
    Detect potential brute force attacks and create alerts.
    """
    from .models import AuditLog, SecurityAlert, BlockedIP
    
    # Look for IPs with many failed logins in the last hour
    one_hour_ago = timezone.now() - timedelta(hours=1)
    
    from django.db.models import Count
    
    suspicious = AuditLog.objects.filter(
        action=AuditLog.Action.FAILED_LOGIN,
        created_at__gte=one_hour_ago
    ).values('ip_address').annotate(
        count=Count('id')
    ).filter(count__gte=10)
    
    alerts_created = 0
    for item in suspicious:
        ip = item['ip_address']
        count = item['count']
        
        # Check if already alerted
        existing = SecurityAlert.objects.filter(
            ip_address=ip,
            status__in=['open', 'investigating'],
            created_at__gte=one_hour_ago
        ).exists()
        
        if not existing:
            SecurityAlert.objects.create(
                title=f'Possible brute force attack from {ip}',
                description=f'{count} failed login attempts in the last hour.',
                severity=SecurityAlert.Severity.HIGH,
                ip_address=ip,
            )
            alerts_created += 1
            
            # Auto-block if more than 20 attempts
            if count >= 20:
                BlockedIP.objects.get_or_create(
                    ip_address=ip,
                    defaults={
                        'reason': BlockedIP.Reason.BRUTE_FORCE,
                        'description': f'Auto-blocked: {count} failed login attempts',
                        'blocked_until': timezone.now() + timedelta(hours=24),
                    }
                )
    
    return f'Created {alerts_created} security alerts.'


@shared_task
def reset_rate_limit_violations():
    """Reset rate limit violation counts daily."""
    from .models import RateLimitViolation
    
    yesterday = timezone.now() - timedelta(days=1)
    
    deleted, _ = RateLimitViolation.objects.filter(
        last_violation__lt=yesterday
    ).delete()
    
    return f'Cleaned up {deleted} old rate limit violations.'
