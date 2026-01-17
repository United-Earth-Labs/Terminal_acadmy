"""
Admin configuration for Lab models.
"""
from django.contrib import admin
from .models import SimulatedEnvironment, Lab, LabAttempt, CommandLog


class LabInline(admin.TabularInline):
    model = Lab
    extra = 0
    show_change_link = True


@admin.register(SimulatedEnvironment)
class SimulatedEnvironmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'simulated_user', 'simulated_hostname', 'created_at']
    search_fields = ['name', 'description']
    inlines = [LabInline]


@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'difficulty', 'xp_reward', 'is_active']
    list_filter = ['difficulty', 'is_active', 'lesson__module__course']
    search_fields = ['title', 'description']
    
    fieldsets = (
        (None, {
            'fields': ('lesson', 'title', 'description', 'instructions')
        }),
        ('Configuration', {
            'fields': ('difficulty', 'xp_reward', 'time_limit', 'environment')
        }),
        ('Lab Content', {
            'fields': ('allowed_commands', 'objectives', 'hints', 'flags'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )


class CommandLogInline(admin.TabularInline):
    model = CommandLog
    extra = 0
    readonly_fields = ['command', 'output', 'was_blocked', 'blocked_reason', 'executed_at']
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(LabAttempt)
class LabAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'lab', 'completed', 'commands_executed', 'started_at']
    list_filter = ['completed', 'lab__lesson__module__course']
    search_fields = ['user__email', 'lab__title']
    readonly_fields = ['started_at', 'completed_at', 'commands_executed']
    inlines = [CommandLogInline]


@admin.register(CommandLog)
class CommandLogAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'command', 'was_blocked', 'executed_at']
    list_filter = ['was_blocked', 'executed_at']
    search_fields = ['command', 'attempt__user__email']
    readonly_fields = ['attempt', 'command', 'output', 'was_blocked', 'blocked_reason', 'executed_at']
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
