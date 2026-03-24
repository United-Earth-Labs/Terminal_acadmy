"""
Security and audit models for Terminal Academy.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class AuditLog(models.Model):
    """
    Comprehensive audit log for security tracking.
    """
    
    class Action(models.TextChoices):
        LOGIN = 'login', _('Login')
        LOGOUT = 'logout', _('Logout')
        FAILED_LOGIN = 'failed_login', _('Failed Login')
        REGISTER = 'register', _('Register')
        PASSWORD_CHANGE = 'password_change', _('Password Change')
        PROFILE_UPDATE = 'profile_update', _('Profile Update')
        LAB_ACCESS = 'lab_access', _('Lab Access')
        COMMAND_EXECUTE = 'command_execute', _('Command Execute')
        ADMIN_ACTION = 'admin_action', _('Admin Action')
        API_REQUEST = 'api_request', _('API Request')
    
    # User (can be null for failed logins)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs'
    )
    
    # Action details
    action = models.CharField(
        _('action'),
        max_length=50,
        choices=Action.choices
    )
    description = models.TextField(_('description'), blank=True)
    
    # Request info
    ip_address = models.GenericIPAddressField(_('IP address'))
    user_agent = models.TextField(_('user agent'), blank=True, default='')
    request_path = models.CharField(_('request path'), max_length=500)
    request_method = models.CharField(_('request method'), max_length=10)
    
    # Response info
    response_status = models.PositiveIntegerField(
        _('response status'),
        null=True,
        blank=True
    )
    
    # Metadata
    extra_data = models.JSONField(_('extra data'), default=dict, blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(_('created at'), auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = _('audit log')
        verbose_name_plural = _('audit logs')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'action']),
            models.Index(fields=['ip_address']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        user_str = self.user.email if self.user else 'Anonymous'
        return f"{self.created_at} - {user_str} - {self.action}"


class BlockedIP(models.Model):
    """
    IP addresses blocked from accessing the platform.
    """
    
    class Reason(models.TextChoices):
        BRUTE_FORCE = 'brute_force', _('Brute Force Attack')
        SUSPICIOUS_ACTIVITY = 'suspicious', _('Suspicious Activity')
        ABUSE = 'abuse', _('Platform Abuse')
        MANUAL = 'manual', _('Manually Blocked')
    
    ip_address = models.GenericIPAddressField(_('IP address'), unique=True)
    reason = models.CharField(
        _('reason'),
        max_length=20,
        choices=Reason.choices,
        default=Reason.MANUAL
    )
    description = models.TextField(_('description'), blank=True)
    
    blocked_at = models.DateTimeField(_('blocked at'), auto_now_add=True)
    blocked_until = models.DateTimeField(
        _('blocked until'),
        null=True,
        blank=True,
        help_text=_('Leave empty for permanent block')
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = _('blocked IP')
        verbose_name_plural = _('blocked IPs')
    
    def __str__(self):
        return f"{self.ip_address} - {self.reason}"
    
    @property
    def is_active(self):
        from django.utils import timezone
        if self.blocked_until is None:
            return True
        return timezone.now() < self.blocked_until


class RateLimitViolation(models.Model):
    """
    Track rate limit violations for monitoring.
    """
    
    ip_address = models.GenericIPAddressField(_('IP address'))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    endpoint = models.CharField(_('endpoint'), max_length=200)
    violation_count = models.PositiveIntegerField(_('violation count'), default=1)
    
    first_violation = models.DateTimeField(_('first violation'), auto_now_add=True)
    last_violation = models.DateTimeField(_('last violation'), auto_now=True)
    
    class Meta:
        verbose_name = _('rate limit violation')
        verbose_name_plural = _('rate limit violations')
        unique_together = ['ip_address', 'endpoint']
    
    def __str__(self):
        return f"{self.ip_address} - {self.endpoint}: {self.violation_count} violations"


class SecurityAlert(models.Model):
    """
    Security alerts for admin review.
    """
    
    class Severity(models.TextChoices):
        LOW = 'low', _('Low')
        MEDIUM = 'medium', _('Medium')
        HIGH = 'high', _('High')
        CRITICAL = 'critical', _('Critical')
    
    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        INVESTIGATING = 'investigating', _('Investigating')
        RESOLVED = 'resolved', _('Resolved')
        FALSE_POSITIVE = 'false_positive', _('False Positive')
    
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'))
    
    severity = models.CharField(
        _('severity'),
        max_length=20,
        choices=Severity.choices,
        default=Severity.MEDIUM
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN
    )
    
    ip_address = models.GenericIPAddressField(_('IP address'), null=True, blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='security_alerts'
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    resolved_at = models.DateTimeField(_('resolved at'), null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resolved_alerts'
    )
    
    class Meta:
        verbose_name = _('security alert')
        verbose_name_plural = _('security alerts')
        ordering = ['-severity', '-created_at']
    
    def __str__(self):
        return f"[{self.severity}] {self.title}"
