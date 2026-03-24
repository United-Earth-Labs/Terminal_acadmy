"""
API views for progress.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import UserProgress, UserXP, XPTransaction, UserAchievement, Achievement
from .serializers import (
    UserProgressSerializer, UserXPSerializer, XPTransactionSerializer,
    UserAchievementSerializer, AchievementSerializer, UserStatsSerializer
)
from .services import get_user_stats


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_stats(request):
    """Get current user's stats."""
    stats = get_user_stats(request.user)
    serializer = UserStatsSerializer(stats)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_xp(request):
    """Get current user's XP details."""
    try:
        user_xp = request.user.xp
        serializer = UserXPSerializer(user_xp)
        return Response(serializer.data)
    except UserXP.DoesNotExist:
        return Response({
            'total_xp': 0,
            'level': 1,
            'xp_for_next_level': 100,
            'xp_progress': 0,
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_xp_history(request):
    """Get current user's XP transaction history."""
    transactions = XPTransaction.objects.filter(
        user=request.user
    ).order_by('-created_at')[:50]
    
    serializer = XPTransactionSerializer(transactions, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_progress(request):
    """Get current user's course progress."""
    progress = UserProgress.objects.filter(
        user=request.user
    ).select_related('course').order_by('-last_accessed')
    
    serializer = UserProgressSerializer(progress, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_achievements(request):
    """Get current user's achievements."""
    achievements = UserAchievement.objects.filter(
        user=request.user
    ).select_related('achievement').order_by('-unlocked_at')
    
    serializer = UserAchievementSerializer(achievements, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_achievements(request):
    """Get all available achievements."""
    achievements = Achievement.objects.filter(is_hidden=False)
    
    # Mark which ones user has unlocked
    unlocked_ids = set(
        UserAchievement.objects.filter(user=request.user).values_list('achievement_id', flat=True)
    )
    
    data = []
    for achievement in achievements:
        item = AchievementSerializer(achievement).data
        item['unlocked'] = achievement.id in unlocked_ids
        data.append(item)
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def leaderboard(request):
    """Get XP leaderboard."""
    top_users = UserXP.objects.select_related('user').order_by('-total_xp')[:50]
    
    data = []
    for i, user_xp in enumerate(top_users):
        data.append({
            'rank': i + 1,
            'user': user_xp.user.display_name,
            'level': user_xp.level,
            'total_xp': user_xp.total_xp,
            'is_current_user': user_xp.user == request.user,
        })
    
    return Response(data)
