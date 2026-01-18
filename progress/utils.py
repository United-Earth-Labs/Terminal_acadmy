"""Utilities for calculating achievement progress."""
from django.db.models import Count


def calculate_achievement_progress(user, achievement):
    """
    Calculate user's progress toward an achievement.
    
    Returns: {
        'current': int,  # Current progress
        'required': int,  # Required to unlock
        'percentage': int,  # 0-100
        'is_unlocked': bool
    }
    """
    from progress.models import LessonProgress, UserXP, Streak, UserAchievement
    from labs.models import LabAttempt
    from courses.models import Course
    
    requirements = achievement.requirements
    req_type = requirements.get('type', '')
    
    # Check if already unlocked
    is_unlocked = UserAchievement.objects.filter(
        user=user,
        achievement=achievement
    ).exists()
    
    # Get required amount
    required = requirements.get('count', requirements.get('amount', requirements.get('days', requirements.get('level', 0))))
    
    if is_unlocked:
        return {
            'current': required,
            'required': required,
            'percentage': 100,
            'is_unlocked': True
        }
    
    # Calculate current progress based on type
    current = 0
    
    if req_type == 'lessons_completed':
        current = LessonProgress.objects.filter(
            user=user,
            completed=True
        ).count()
        
    elif req_type == 'labs_completed':
        current = LabAttempt.objects.filter(
            user=user,
            completed=True
        ).count()
        
    elif req_type == 'total_xp':
        user_xp = UserXP.objects.filter(user=user).first()
        current = user_xp.total_xp if user_xp else 0
        
    elif req_type == 'streak_days':
        streak = Streak.objects.filter(user=user).first()
        current = max(streak.current_streak, streak.longest_streak) if streak else 0
        
    elif req_type == 'courses_completed':
        # Count courses where all lessons are completed
        for course in Course.objects.filter(status='published'):
            total_lessons = sum(module.lessons.count() for module in course.modules.all())
            if total_lessons == 0:
                continue
            completed_lessons = LessonProgress.objects.filter(
                user=user,
                lesson__module__course=course,
                completed=True
            ).count()
            if completed_lessons >= total_lessons:
                current += 1
                
    elif req_type == 'level_reached':
        user_xp = UserXP.objects.filter(user=user).first()
        current = user_xp.level if user_xp else 1
        
    else:
        # Unknown type, can't calculate
        return {
            'current': 0,
            'required': 0,
            'percentage': 0,
            'is_unlocked': False
        }
    
    percentage = min(100, int(current / required * 100)) if required > 0 else 0
    
    return {
        'current': current,
        'required': required,
        'percentage': percentage,
        'is_unlocked': False
    }
