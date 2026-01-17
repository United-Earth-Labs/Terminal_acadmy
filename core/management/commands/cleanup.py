"""
Django management commands to replace Celery tasks.
Run these with: python manage.py <command_name>

For PythonAnywhere, set up scheduled tasks in the dashboard.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Cleanup expired sessions and old data'

    def handle(self, *args, **options):
        self.stdout.write('Running cleanup tasks...')
        
        # 1. Cleanup expired sessions
        from users.models import UserSession
        expired = UserSession.objects.filter(expires_at__lt=timezone.now())
        count = expired.count()
        expired.delete()
        self.stdout.write(f'  Deleted {count} expired sessions')
        
        # 2. Unlock expired account locks
        from users.models import CustomUser
        locked = CustomUser.objects.filter(
            account_locked_until__lt=timezone.now()
        )
        unlocked = locked.update(account_locked_until=None, failed_login_attempts=0)
        self.stdout.write(f'  Unlocked {unlocked} accounts')
        
        # 3. Reset broken streaks
        from progress.models import Streak
        from datetime import date
        yesterday = date.today() - timedelta(days=1)
        broken = Streak.objects.filter(
            last_activity_date__lt=yesterday,
            current_streak__gt=0
        )
        reset = broken.update(current_streak=0)
        self.stdout.write(f'  Reset {reset} broken streaks')
        
        # 4. Cleanup old audit logs (90 days)
        from security.models import AuditLog
        cutoff = timezone.now() - timedelta(days=90)
        deleted, _ = AuditLog.objects.filter(created_at__lt=cutoff).delete()
        self.stdout.write(f'  Deleted {deleted} old audit logs')
        
        # 5. Remove expired IP blocks
        from security.models import BlockedIP
        deleted, _ = BlockedIP.objects.filter(
            blocked_until__lt=timezone.now()
        ).delete()
        self.stdout.write(f'  Removed {deleted} expired IP blocks')
        
        self.stdout.write(self.style.SUCCESS('Cleanup complete!'))
