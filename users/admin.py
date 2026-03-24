"""
Admin configuration for User models.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser, UserSession


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Admin configuration for CustomUser model."""
    
    list_display = [
        'email', 'first_name', 'last_name', 'role', 
        'skill_level', 'ethical_agreement_accepted', 'is_active'
    ]
    list_filter = [
        'role', 'skill_level', 'ethical_agreement_accepted', 
        'is_active', 'is_staff', 'created_at'
    ]
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'bio', 'avatar')
        }),
        (_('Role & Skills'), {
            'fields': ('role', 'skill_level')
        }),
        (_('Ethical Agreement'), {
            'fields': (
                'ethical_agreement_accepted',
                'ethical_agreement_accepted_at',
                'ethical_agreement_ip'
            )
        }),
        (_('Security'), {
            'fields': (
                'last_login_ip',
                'failed_login_attempts',
                'account_locked_until',
                'otp_enabled',
                'otp_secret'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            ),
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'role'),
        }),
    )
    
    readonly_fields = [
        'last_login', 'date_joined', 'created_at', 'updated_at',
        'ethical_agreement_accepted_at', 'ethical_agreement_ip'
    ]


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin configuration for UserSession model."""
    
    list_display = ['user', 'ip_address', 'created_at', 'last_activity', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__email', 'ip_address']
    readonly_fields = ['session_key', 'created_at', 'last_activity']
    
    def has_add_permission(self, request):
        return False
