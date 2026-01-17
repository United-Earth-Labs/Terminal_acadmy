"""
Admin configuration for Security models.
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import AuditLog, BlockedIP, RateLimitViolation, SecurityAlert


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'user', 'action', 'ip_address', 'request_path', 'response_status']
    list_filter = ['action', 'response_status', 'created_at']
    search_fields = ['user__email', 'ip_address', 'request_path']
    readonly_fields = [
        'user', 'action', 'description', 'ip_address', 'user_agent',
        'request_path', 'request_method', 'response_status', 'extra_data', 'created_at'
    ]
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete audit logs
        return request.user.is_superuser


@admin.register(BlockedIP)
class BlockedIPAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'reason', 'blocked_at', 'blocked_until', 'is_active_display']
    list_filter = ['reason', 'blocked_at']
    search_fields = ['ip_address', 'description']
    
    def is_active_display(self, obj):
        if obj.is_active:
            return format_html('<span style="color: red;">● Blocked</span>')
        return format_html('<span style="color: green;">○ Expired</span>')
    is_active_display.short_description = 'Status'


@admin.register(RateLimitViolation)
class RateLimitViolationAdmin(admin.ModelAdmin):
    list_display = ['ip_address', 'endpoint', 'violation_count', 'first_violation', 'last_violation']
    list_filter = ['endpoint', 'first_violation']
    search_fields = ['ip_address', 'user__email']
    readonly_fields = ['ip_address', 'user', 'endpoint', 'violation_count', 'first_violation', 'last_violation']


@admin.register(SecurityAlert)
class SecurityAlertAdmin(admin.ModelAdmin):
    list_display = ['title', 'severity_display', 'status', 'ip_address', 'created_at']
    list_filter = ['severity', 'status', 'created_at']
    search_fields = ['title', 'description', 'ip_address']
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'severity', 'status')
        }),
        ('Related', {
            'fields': ('ip_address', 'user')
        }),
        ('Resolution', {
            'fields': ('resolved_at', 'resolved_by'),
            'classes': ('collapse',)
        }),
    )
    
    def severity_display(self, obj):
        colors = {
            'low': 'blue',
            'medium': 'orange',
            'high': 'red',
            'critical': 'darkred',
        }
        color = colors.get(obj.severity, 'gray')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_severity_display()
        )
    severity_display.short_description = 'Severity'
