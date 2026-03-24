"""
User services for business logic.
"""
from typing import Optional, Dict
from datetime import timedelta
from django.utils import timezone
from courses.models import AssessmentSession, AssessmentAuditLog


# Rate limiting configuration
SKILL_ASSESSMENT_COOLDOWN_HOURS = 24  # 24 hour cooldown between attempts


def get_client_ip(request) -> Optional[str]:
    """Extract client IP address from request."""
    if not request:
        return None
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request) -> str:
    """Extract user agent from request."""
    if not request:
        return ''
    return request.META.get('HTTP_USER_AGENT', '')


def check_skill_assessment_rate_limit(user, request=None) -> Dict:
    """
    Check if user can take skill assessment based on rate limiting.
    
    Args:
        user: User attempting the assessment
        request: HTTP request (optional)
    
    Returns:
        Dictionary with 'allowed', 'error', and optional 'cooldown_remaining'
    """
    # Check if user has already completed assessment
    if user.skill_assessment_completed_at:
        # Check when they last completed it
        time_since_completion = timezone.now() - user.skill_assessment_completed_at
        cooldown_period = timedelta(hours=SKILL_ASSESSMENT_COOLDOWN_HOURS)
        
        if time_since_completion < cooldown_period:
            remaining = cooldown_period - time_since_completion
            hours_remaining = remaining.total_seconds() / 3600
            
            # Log rate limit hit
            from courses.services import log_assessment_event
            log_assessment_event(
                user=user,
                event_type=AssessmentAuditLog.EventType.RATE_LIMIT_HIT,
                severity=AssessmentAuditLog.Severity.WARNING,
                message=f"Skill assessment rate limit hit. {hours_remaining:.1f} hours remaining",
                request=request,
                metadata={
                    'last_completion': user.skill_assessment_completed_at.isoformat(),
                    'cooldown_hours': SKILL_ASSESSMENT_COOLDOWN_HOURS,
                    'hours_remaining': hours_remaining
                }
            )
            
            return {
                'allowed': False,
                'error': f'You can retake the skill assessment in {hours_remaining:.1f} hours. Cooldown period: {SKILL_ASSESSMENT_COOLDOWN_HOURS} hours.',
                'cooldown_remaining_hours': hours_remaining
            }
    
    return {
        'allowed': True,
        'error': None
    }


def create_skill_assessment_session(user, request=None) -> Dict:
    """
    Create a new skill assessment session with tracking.
    
    Args:
        user: User taking the assessment
        request: HTTP request (optional)
    
    Returns:
        Dictionary with 'session' and session info
    """
    import secrets
    
    # Generate session token
    session_token = secrets.token_urlsafe(32)
    
    # 1 hour expiration for skill assessment
    expires_at = timezone.now() + timedelta(hours=1)
    
    # Extract request metadata
    ip_address = get_client_ip(request)
    user_agent = get_user_agent(request)
    
    # Deactivate any existing active skill assessment sessions
    AssessmentSession.objects.filter(
        user=user,
        session_type=AssessmentSession.SessionType.SKILL_ASSESSMENT,
        is_active=True,
        submitted=False
    ).update(is_active=False)
    
    # Create new session
    session = AssessmentSession.objects.create(
        user=user,
        session_type=AssessmentSession.SessionType.SKILL_ASSESSMENT,
        session_token=session_token,
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    # Log session creation
    from courses.services import log_assessment_event
    log_assessment_event(
        user=user,
        event_type=AssessmentAuditLog.EventType.SESSION_CREATED,
        severity=AssessmentAuditLog.Severity.INFO,
        message="Skill assessment session created",
        session=session,
        request=request,
        metadata={'expires_at': expires_at.isoformat()}
    )
    
    return {
        'session': session,
        'session_token': session_token,
        'expires_at': expires_at,
    }


def process_skill_assessment(answers: Dict, user=None, request=None) -> Dict:
    """
    Process skill assessment answers and return the appropriate skill level.
    
    Enhanced with:
    - Comprehensive validation
    - Audit logging
    - Security tracking
    
    Args:
        answers: Dictionary of question_id -> answer
        user: User taking the assessment (optional, for logging)
        request: HTTP request (optional, for IP/user agent tracking)
    
    Returns:
        Dictionary with 'success', 'skill_level', 'error', 'score', 'total'
    """
    from courses.services import log_assessment_event
    
    # Define expected questions and valid answer values
    EXPECTED_QUESTIONS = ['q1', 'q2', 'q3', 'q4', 'q5']
    VALID_ANSWERS = ['correct', 'wrong', 'unsure']
    
    # Validate all questions are answered
    missing_questions = [q for q in EXPECTED_QUESTIONS if q not in answers]
    if missing_questions:
        if user:
            log_assessment_event(
                user=user,
                event_type=AssessmentAuditLog.EventType.VALIDATION_ERROR,
                severity=AssessmentAuditLog.Severity.ERROR,
                message=f"Missing questions: {', '.join(missing_questions)}",
                request=request,
                metadata={'missing_questions': missing_questions}
            )
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
            if user:
                log_assessment_event(
                    user=user,
                    event_type=AssessmentAuditLog.EventType.VALIDATION_ERROR,
                    severity=AssessmentAuditLog.Severity.ERROR,
                    message=f"Invalid answer value: {key}={value}",
                    request=request,
                    metadata={'question': key, 'invalid_value': value}
                )
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
    
    # Log successful submission
    if user:
        log_assessment_event(
            user=user,
            event_type=AssessmentAuditLog.EventType.SUBMISSION_SUCCESS,
            severity=AssessmentAuditLog.Severity.INFO,
            message=f"Skill assessment completed: {skill_level} ({score}/{total_questions})",
            request=request,
            metadata={
                'skill_level': skill_level,
                'score': score,
                'total': total_questions,
                'percentage': percentage
            }
        )
    
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
