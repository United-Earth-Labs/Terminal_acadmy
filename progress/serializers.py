"""
Serializers for Progress API.
"""
from rest_framework import serializers
from .models import (
    UserProgress, UserXP, XPTransaction,
    Achievement, UserAchievement, Streak
)


class UserProgressSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)
    course_slug = serializers.CharField(source='course.slug', read_only=True)
    
    class Meta:
        model = UserProgress
        fields = ['id', 'course', 'course_title', 'course_slug', 
                  'percentage', 'started_at', 'last_accessed', 'completed_at']


class UserXPSerializer(serializers.ModelSerializer):
    xp_for_next_level = serializers.ReadOnlyField()
    xp_progress = serializers.ReadOnlyField()
    
    class Meta:
        model = UserXP
        fields = ['total_xp', 'level', 'xp_for_next_level', 'xp_progress']


class XPTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = XPTransaction
        fields = ['id', 'amount', 'reason', 'created_at']


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = ['id', 'name', 'slug', 'description', 'category',
                  'xp_reward', 'badge_image', 'is_rare']


class UserAchievementSerializer(serializers.ModelSerializer):
    achievement = AchievementSerializer(read_only=True)
    
    class Meta:
        model = UserAchievement
        fields = ['id', 'achievement', 'unlocked_at']


class StreakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Streak
        fields = ['current_streak', 'longest_streak', 'last_activity_date']


class UserStatsSerializer(serializers.Serializer):
    xp = serializers.IntegerField()
    level = serializers.IntegerField()
    xp_progress = serializers.IntegerField()
    xp_for_next_level = serializers.IntegerField()
    streak = serializers.IntegerField()
    longest_streak = serializers.IntegerField()
    courses_completed = serializers.IntegerField()
    courses_in_progress = serializers.IntegerField()
    labs_completed = serializers.IntegerField()
    achievements_count = serializers.IntegerField()
