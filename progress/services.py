"""
Progress services for XP and achievement management.
"""
from django.utils import timezone
from datetime import date

from .models import UserXP, XPTransaction, Achievement, UserAchievement, Streak


def award_xp(user, amount: int, reason: str):
    """
    Award XP to a user.
    
    Args:
        user: The user to award XP to
        amount: Amount of XP to award
        reason: Description of why XP was awarded
    """
    # Get or create UserXP
    user_xp, created = UserXP.objects.get_or_create(user=user)
    
    # Add XP
    user_xp.total_xp += amount
    
    # Check for level up
    while user_xp.total_xp >= sum(i * 100 for i in range(1, user_xp.level + 1)):
        user_xp.level += 1
    
    user_xp.save()
    
    # Log transaction
    XPTransaction.objects.create(
        user=user,
        amount=amount,
        reason=reason
    )
    
    # Check achievements
    check_achievements(user)
    
    # Update streak
    update_streak(user)
    
    return user_xp


def update_streak(user):
    """
    Update user's learning streak.
    """
    streak, _ = Streak.objects.get_or_create(user=user)
    today = date.today()
    
    if streak.last_activity_date is None:
        # First activity
        streak.current_streak = 1
    elif streak.last_activity_date == today:
        # Already logged today
        return
    elif (today - streak.last_activity_date).days == 1:
        # Consecutive day
        streak.current_streak += 1
    else:
        # Streak broken
        streak.current_streak = 1
    
    streak.last_activity_date = today
    
    if streak.current_streak > streak.longest_streak:
        streak.longest_streak = streak.current_streak
    
    streak.save()


def check_achievements(user):
    """
    Check if user has unlocked any new achievements.
    """
    # Get achievements user hasn't unlocked
    unlocked_ids = UserAchievement.objects.filter(user=user).values_list('achievement_id', flat=True)
    available = Achievement.objects.exclude(id__in=unlocked_ids)
    
    for achievement in available:
        if check_achievement_requirements(user, achievement):
            unlock_achievement(user, achievement)


def check_achievement_requirements(user, achievement) -> bool:
    """
    Check if a user meets the requirements for an achievement.
    """
    requirements = achievement.requirements
    
    if not requirements:
        return False
    
    req_type = requirements.get('type')
    
    if req_type == 'xp':
        # Requires minimum XP
        min_xp = requirements.get('amount', 0)
        try:
            return user.xp.total_xp >= min_xp
        except UserXP.DoesNotExist:
            return False
    
    elif req_type == 'level':
        # Requires minimum level
        min_level = requirements.get('level', 1)
        try:
            return user.xp.level >= min_level
        except UserXP.DoesNotExist:
            return False
    
    elif req_type == 'courses_completed':
        # Requires completing N courses
        from .models import UserProgress
        count = requirements.get('count', 1)
        completed = UserProgress.objects.filter(
            user=user,
            percentage=100
        ).count()
        return completed >= count
    
    elif req_type == 'labs_completed':
        # Requires completing N labs
        from labs.models import LabAttempt
        count = requirements.get('count', 1)
        completed = LabAttempt.objects.filter(
            user=user,
            completed=True
        ).count()
        return completed >= count
    
    elif req_type == 'streak':
        # Requires N-day streak
        days = requirements.get('days', 1)
        try:
            return user.streak.current_streak >= days
        except Streak.DoesNotExist:
            return False
    
    return False


def unlock_achievement(user, achievement):
    """
    Unlock an achievement for a user.
    """
    UserAchievement.objects.get_or_create(
        user=user,
        achievement=achievement
    )
    
    # Award XP for the achievement
    if achievement.xp_reward > 0:
        XPTransaction.objects.create(
            user=user,
            amount=achievement.xp_reward,
            reason=f'Achievement unlocked: {achievement.name}'
        )
        
        try:
            user_xp = user.xp
            user_xp.total_xp += achievement.xp_reward
            user_xp.save()
        except UserXP.DoesNotExist:
            pass


def get_user_stats(user) -> dict:
    """
    Get comprehensive stats for a user.
    """
    from .models import UserProgress
    from labs.models import LabAttempt
    
    try:
        user_xp = user.xp
        xp = user_xp.total_xp
        level = user_xp.level
        xp_progress = user_xp.xp_progress
        xp_for_next = user_xp.xp_for_next_level
    except UserXP.DoesNotExist:
        xp = 0
        level = 1
        xp_progress = 0
        xp_for_next = 100
    
    try:
        streak = user.streak.current_streak
        longest_streak = user.streak.longest_streak
    except Streak.DoesNotExist:
        streak = 0
        longest_streak = 0
    
    courses_completed = UserProgress.objects.filter(
        user=user,
        percentage=100
    ).count()
    
    courses_in_progress = UserProgress.objects.filter(
        user=user,
        percentage__gt=0,
        percentage__lt=100
    ).count()
    
    labs_completed = LabAttempt.objects.filter(
        user=user,
        completed=True
    ).count()
    
    achievements_count = UserAchievement.objects.filter(user=user).count()
    
    return {
        'xp': xp,
        'level': level,
        'xp_progress': xp_progress,
        'xp_for_next_level': xp_for_next,
        'streak': streak,
        'longest_streak': longest_streak,
        'courses_completed': courses_completed,
        'courses_in_progress': courses_in_progress,
        'labs_completed': labs_completed,
        'achievements_count': achievements_count,
    }
