"""
Admin configuration for Progress models.
"""
from django.contrib import admin
from .models import (
    UserProgress, ModuleProgress, LessonProgress,
    UserXP, XPTransaction, Achievement, UserAchievement, Streak
)


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'percentage', 'started_at', 'completed_at']
    list_filter = ['course', 'percentage']
    search_fields = ['user__email', 'course__title']


@admin.register(ModuleProgress)
class ModuleProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'module', 'completed', 'completed_at']
    list_filter = ['completed', 'module__course']
    search_fields = ['user__email', 'module__title']


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'started', 'completed', 'xp_awarded']
    list_filter = ['completed', 'xp_awarded']
    search_fields = ['user__email', 'lesson__title']


@admin.register(UserXP)
class UserXPAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_xp', 'level']
    search_fields = ['user__email']
    ordering = ['-total_xp']


@admin.register(XPTransaction)
class XPTransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'reason', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'reason']
    readonly_fields = ['user', 'amount', 'reason', 'created_at']


@admin.register(Achievement)
class AchievementAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'xp_reward', 'is_hidden', 'is_rare']
    list_filter = ['category', 'is_hidden', 'is_rare']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ['user', 'achievement', 'unlocked_at']
    list_filter = ['achievement']
    search_fields = ['user__email', 'achievement__name']


@admin.register(Streak)
class StreakAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_streak', 'longest_streak', 'last_activity_date']
    search_fields = ['user__email']
    ordering = ['-current_streak']
