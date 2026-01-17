"""
User services for business logic.
"""
from typing import Optional, Dict


def process_skill_assessment(answers: Dict) -> Dict:
    """
    Process skill assessment answers and return the appropriate skill level.
    
    Args:
        answers: Dictionary of question_id -> answer
    
    Returns:
        Dictionary with 'success', 'skill_level', 'error', 'score', 'total'
    """
    # Define expected questions and valid answer values
    EXPECTED_QUESTIONS = ['q1', 'q2', 'q3', 'q4', 'q5']
    VALID_ANSWERS = ['correct', 'wrong', 'unsure']
    
    # Validate all questions are answered
    missing_questions = [q for q in EXPECTED_QUESTIONS if q not in answers]
    if missing_questions:
        return {
            'success': False,
            'error': f'Please answer all questions. Missing: {", ".join(missing_questions)}',
            'skill_level': None,
            'score': 0,
            'total': len(EXPECTED_QUESTIONS)
        }
    
    # Validate answer values
    for key, value in answers.items():
        if key.startswith('q') and value not in VALID_ANSWERS:
            return {
                'success': False,
                'error': f'Invalid answer value for {key}: {value}',
                'skill_level': None,
                'score': 0,
                'total': len(EXPECTED_QUESTIONS)
            }
    
    # Score each answer
    score = 0
    for question in EXPECTED_QUESTIONS:
        if answers.get(question) == 'correct':
            score += 1
    
    total_questions = len(EXPECTED_QUESTIONS)
    percentage = (score / total_questions) * 100
    
    # Determine skill level
    if percentage >= 90:
        skill_level = 'expert'
    elif percentage >= 70:
        skill_level = 'advanced'
    elif percentage >= 40:
        skill_level = 'intermediate'
    else:
        skill_level = 'beginner'
    
    return {
        'success': True,
        'skill_level': skill_level,
        'error': None,
        'score': score,
        'total': total_questions
    }


def get_user_statistics(user) -> Dict:
    """
    Get statistics for a user.
    
    Args:
        user: The user object
    
    Returns:
        Dictionary of user statistics
    """
    from progress.models import UserProgress, UserXP
    
    try:
        user_xp = UserXP.objects.get(user=user)
        xp = user_xp.total_xp
        level = user_xp.level
    except UserXP.DoesNotExist:
        xp = 0
        level = 1
    
    courses_in_progress = UserProgress.objects.filter(
        user=user,
        percentage__gt=0,
        percentage__lt=100
    ).count()
    
    courses_completed = UserProgress.objects.filter(
        user=user,
        percentage=100
    ).count()
    
    return {
        'xp': xp,
        'level': level,
        'courses_in_progress': courses_in_progress,
        'courses_completed': courses_completed,
        'skill_level': user.skill_level,
    }
