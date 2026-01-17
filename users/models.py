"""
Custom User models for Terminal Academy.

This module contains the custom user model and related models
for authentication, authorization, and user management.
"""
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """Custom manager for CustomUser model using email as the unique identifier."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Custom User model for Terminal Academy.
    
    Uses email as the unique identifier instead of username.
    Includes role-based access control and ethical agreement tracking.
    """
    
    class Role(models.TextChoices):
        STUDENT = 'student', _('Student')
        MENTOR = 'mentor', _('Mentor')
        ADMIN = 'admin', _('Administrator')
    
    class SkillLevel(models.TextChoices):
        NOT_ASSESSED = 'not_assessed', _('Not Assessed')
        BEGINNER = 'beginner', _('Beginner')
        INTERMEDIATE = 'intermediate', _('Intermediate')
        ADVANCED = 'advanced', _('Advanced')
        EXPERT = 'expert', _('Expert')
    
    # Override username to allow null (we use email as identifier)
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        null=True,
        blank=True,
    )
    
    # Email is the primary identifier
    email = models.EmailField(_('email address'), unique=True)
    
    # Role and skill tracking
    role = models.CharField(
        _('role'),
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    skill_level = models.CharField(
        _('skill level'),
        max_length=20,
        choices=SkillLevel.choices,
        default=SkillLevel.NOT_ASSESSED,
    )
    skill_assessment_completed_at = models.DateTimeField(
        _('skill assessment completed at'),
        null=True,
        blank=True,
    )
    
    # Ethical agreement (CRITICAL for legal compliance)
    ethical_agreement_accepted = models.BooleanField(
        _('ethical agreement accepted'),
        default=False,
    )
    ethical_agreement_accepted_at = models.DateTimeField(
        _('ethical agreement accepted at'),
        null=True,
        blank=True,
    )
    ethical_agreement_ip = models.GenericIPAddressField(
        _('ethical agreement IP'),
        null=True,
        blank=True,
    )
    
    # Security tracking
    last_login_ip = models.GenericIPAddressField(
        _('last login IP'),
        null=True,
        blank=True,
    )
    failed_login_attempts = models.PositiveIntegerField(
        _('failed login attempts'),
        default=0,
    )
    account_locked_until = models.DateTimeField(
        _('account locked until'),
        null=True,
        blank=True,
    )
    
    # OTP for two-factor authentication
    otp_secret = models.CharField(
        _('OTP secret'),
        max_length=32,
        blank=True,
        default='',
    )
    otp_enabled = models.BooleanField(
        _('OTP enabled'),
        default=False,
    )
    
    # Profile information
    bio = models.TextField(_('bio'), blank=True, default='')
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/',
        null=True,
        blank=True,
    )
    
    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    @property
    def is_account_locked(self):
        """Check if the account is currently locked."""
        if self.account_locked_until is None:
            return False
        return timezone.now() < self.account_locked_until
    
    def accept_ethical_agreement(self, ip_address=None):
        """Record acceptance of the ethical hacking agreement."""
        self.ethical_agreement_accepted = True
        self.ethical_agreement_accepted_at = timezone.now()
        self.ethical_agreement_ip = ip_address
        self.save(update_fields=[
            'ethical_agreement_accepted',
            'ethical_agreement_accepted_at',
            'ethical_agreement_ip',
        ])
    
    def record_failed_login(self):
        """Record a failed login attempt and lock account if necessary."""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.account_locked_until = timezone.now() + timezone.timedelta(minutes=30)
        
        self.save(update_fields=['failed_login_attempts', 'account_locked_until'])
    
    def record_successful_login(self, ip_address=None):
        """Record a successful login and reset failed attempts."""
        self.failed_login_attempts = 0
        self.account_locked_until = None
        self.last_login_ip = ip_address
        self.last_login = timezone.now()
        self.save(update_fields=[
            'failed_login_attempts',
            'account_locked_until',
            'last_login_ip',
            'last_login',
        ])
    
    @property
    def display_name(self):
        """Return the user's display name."""
        if self.first_name:
            return f"{self.first_name} {self.last_name}".strip()
        return self.email.split('@')[0]


class UserSession(models.Model):
    """
    Track active user sessions for security auditing.
    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='sessions',
    )
    session_key = models.CharField(_('session key'), max_length=40, unique=True)
    ip_address = models.GenericIPAddressField(_('IP address'))
    user_agent = models.TextField(_('user agent'), blank=True, default='')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    last_activity = models.DateTimeField(_('last activity'), auto_now=True)
    is_active = models.BooleanField(_('is active'), default=True)
    
    class Meta:
        verbose_name = _('user session')
        verbose_name_plural = _('user sessions')
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"{self.user.email} - {self.ip_address}"
