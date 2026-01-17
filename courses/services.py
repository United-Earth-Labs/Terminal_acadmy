"""
Business logic for quiz submission and scoring.
"""
import secrets
from typing import Dict, List, Optional
from datetime import timedelta
from django.utils import timezone
from .models import (
    Quiz, QuizQuestion, QuizAnswer, QuizAttempt,
    AssessmentSession, AssessmentAuditLog
)


# Configurable constants
MINIMUM_QUIZ_TIME_SECONDS = 30  # Minimum time to complete a quiz
SUSPICIOUSLY_FAST_SECONDS = 5  # Flag submissions faster than this
SESSION_GRACE_PERIOD_MINUTES = 5  # Extra time after quiz time limit


def get_client_ip(request) -> Optional[str]:
    """Extract client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request) -> str:
    """Extract user agent from request."""
    return request.META.get('HTTP_USER_AGENT', '')


def create_quiz_session(quiz: Quiz, user, request=None) -> Dict:
    """
    Create a new quiz session with tracking token.
    
    Args:
        quiz: Quiz instance
        user: User taking the quiz
        request: HTTP request (optional, for IP/user agent tracking)
    
    Returns:
        Dictionary with 'session' and 'session_token'
    """
    # Generate unique session token
    session_token = secrets.token_urlsafe(32)
    
    # Calculate expiration time
    if quiz.time_limit:
        expires_at = timezone.now() + timedelta(
            minutes=quiz.time_limit + SESSION_GRACE_PERIOD_MINUTES
        )
    else:
        # Default 2 hour expiration for untimed quizzes
        expires_at = timezone.now() + timedelta(hours=2)
    
    # Extract request metadata
    ip_address = get_client_ip(request) if request else None
    user_agent = get_user_agent(request) if request else ''
    
    # Deactivate any existing active sessions for this user/quiz
    AssessmentSession.objects.filter(
        user=user,
        quiz=quiz,
        is_active=True,
        submitted=False
    ).update(is_active=False)
    
    # Create new session
    session = AssessmentSession.objects.create(
        user=user,
        session_type=AssessmentSession.SessionType.QUIZ,
        quiz=quiz,
        session_token=session_token,
        expires_at=expires_at,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    
    # Log session creation
    log_assessment_event(
        user=user,
        event_type=AssessmentAuditLog.EventType.SESSION_CREATED,
        severity=AssessmentAuditLog.Severity.INFO,
        message=f"Quiz session created for: {quiz.title}",
        quiz=quiz,
        session=session,
        request=request,
        metadata={'expires_at': expires_at.isoformat()}
    )
    
    return {
        'session': session,
        'session_token': session_token,
        'expires_at': expires_at,
    }


def validate_quiz_session(session_token: str, quiz: Quiz, user, request=None) -> Dict:
    """
    Validate quiz session token and check for hijacking attempts.
    
    Args:
        session_token: Session token to validate
        quiz: Quiz instance
        user: User submitting the quiz
        request: HTTP request (optional)
    
    Returns:
        Dictionary with 'valid', 'error', 'session', and optional 'severity'
    """
    try:
        session = AssessmentSession.objects.get(session_token=session_token)
    except AssessmentSession.DoesNotExist:
        log_assessment_event(
            user=user,
            event_type=AssessmentAuditLog.EventType.SESSION_HIJACK_ATTEMPT,
            severity=AssessmentAuditLog.Severity.CRITICAL,
            message="Invalid session token provided",
            quiz=quiz,
            request=request,
            metadata={'provided_token': session_token[:10] + '...'}
        )
        return {
            'valid': False,
            'error': 'Invalid session token.',
            'severity': 'critical'
        }
    
    # Check if session belongs to this user
    if session.user != user:
        log_assessment_event(
            user=user,
            event_type=AssessmentAuditLog.EventType.SESSION_HIJACK_ATTEMPT,
            severity=AssessmentAuditLog.Severity.CRITICAL,
            message=f"User {user.email} attempted to use session belonging to {session.user.email}",
            quiz=quiz,
            session=session,
            request=request
        )
        return {
            'valid': False,
            'error': 'Session does not belong to you.',
            'severity': 'critical'
        }
    
    # Check if session is for this quiz
    if session.quiz != quiz:
        log_assessment_event(
            user=user,
            event_type=AssessmentAuditLog.EventType.VALIDATION_ERROR,
            severity=AssessmentAuditLog.Severity.ERROR,
            message=f"Session mismatch: expected {quiz.title}, got {session.quiz.title}",
            quiz=quiz,
            session=session,
            request=request
        )
        return {
            'valid': False,
            'error': 'Session is for a different quiz.',
            'severity': 'error'
        }
    
    # Check if session is active
    if not session.is_active:
        return {
            'valid': False,
            'error': 'Session is no longer active.'
        }
    
    # Check if already submitted
    if session.submitted:
        return {
            'valid': False,
            'error': 'This session has already been submitted.'
        }
    
    # Check if expired
    if session.is_expired():
        log_assessment_event(
            user=user,
            event_type=AssessmentAuditLog.EventType.TIME_LIMIT_EXCEEDED,
            severity=AssessmentAuditLog.Severity.WARNING,
            message="Session expired",
            quiz=quiz,
            session=session,
            request=request
        )
        session.deactivate()
        return {
            'valid': False,
            'error': 'Session has expired.'
        }
    
    return {
        'valid': True,
        'session': session,
        'error': None
    }


def detect_suspicious_timing(session: AssessmentSession, request=None) -> Dict:
    """
    Detect suspiciously fast quiz completion.
    
    Args:
        session: Assessment session
        request: HTTP request (optional)
    
    Returns:
        Dictionary with 'suspicious', 'reason', and 'time_taken'
    """
    time_taken = (timezone.now() - session.started_at).total_seconds()
    
    result = {
        'suspicious': False,
        'reason': None,
        'time_taken': time_taken
    }
    
    # Check if extremely fast (likely automated)
    if time_taken < SUSPICIOUSLY_FAST_SECONDS:
        result['suspicious'] = True
        result['reason'] = f'Completed in {time_taken:.1f}s (suspiciously fast)'
        
        log_assessment_event(
            user=session.user,
            event_type=AssessmentAuditLog.EventType.SUSPICIOUS_TIMING,
            severity=AssessmentAuditLog.Severity.CRITICAL,
            message=f"Extremely fast completion: {time_taken:.1f} seconds",
            quiz=session.quiz,
            session=session,
            request=request,
            metadata={'time_taken': time_taken}
        )
    
    # Check if faster than minimum time
    elif time_taken < MINIMUM_QUIZ_TIME_SECONDS:
        result['suspicious'] = True
        result['reason'] = f'Completed in {time_taken:.1f}s (below {MINIMUM_QUIZ_TIME_SECONDS}s minimum)'
        
        log_assessment_event(
            user=session.user,
            event_type=AssessmentAuditLog.EventType.MINIMUM_TIME_VIOLATION,
            severity=AssessmentAuditLog.Severity.WARNING,
            message=f"Minimum time violation: {time_taken:.1f} seconds",
            quiz=session.quiz,
            session=session,
            request=request,
            metadata={'time_taken': time_taken, 'minimum_required': MINIMUM_QUIZ_TIME_SECONDS}
        )
    
    return result


def log_assessment_event(
    user,
    event_type: str,
    severity: str,
    message: str,
    quiz=None,
    session=None,
    request=None,
    metadata: Dict = None
):
    """
    Log an assessment-related event to the audit log.
    
    Args:
        user: User involved in the event
        event_type: Type of event (from AssessmentAuditLog.EventType)
        severity: Severity level (from AssessmentAuditLog.Severity)
        message: Human-readable message
        quiz: Quiz instance (optional)
        session: Assessment session (optional)
        request: HTTP request (optional, for IP/user agent)
        metadata: Additional metadata dictionary (optional)
    """
    ip_address = get_client_ip(request) if request else None
    user_agent = get_user_agent(request) if request else ''
    
    AssessmentAuditLog.objects.create(
        user=user,
        session=session,
        quiz=quiz,
        event_type=event_type,
        severity=severity,
        message=message,
        metadata=metadata or {},
        ip_address=ip_address,
        user_agent=user_agent
    )


def validate_quiz_submission(quiz: Quiz, user, answers: Dict) -> Dict:
    """
    Validate a quiz submission before processing.
    
    Args:
        quiz: Quiz instance
        user: User submitting the quiz
        answers: Dictionary mapping question IDs to answer ID lists
    
    Returns:
        Dictionary with 'valid', 'error', and optional 'data'
    """
    # Check attempt limits
    attempt_count = QuizAttempt.objects.filter(
        user=user,
        quiz=quiz,
        submitted_at__isnull=False
    ).count()
    
    if attempt_count >= quiz.max_attempts:
        return {
            'valid': False,
            'error': f'Maximum attempts ({quiz.max_attempts}) exceeded for this quiz.'
        }
    
    # Validate all questions are answered
    question_ids = set(quiz.questions.values_list('id', flat=True))
    answered_ids = set(int(qid) for qid in answers.keys() if qid.isdigit())
    
    if not question_ids.issubset(answered_ids):
        missing = question_ids - answered_ids
        return {
            'valid': False,
            'error': f'Please answer all questions. Missing {len(missing)} question(s).'
        }
    
    # Validate answer IDs belong to their questions
    for question_id, answer_ids in answers.items():
        if not question_id.isdigit():
            continue
            
        question_id = int(question_id)
        if question_id not in question_ids:
            return {
                'valid': False,
                'error': f'Invalid question ID: {question_id}'
            }
        
        # Convert answer_ids to list if single value
        if not isinstance(answer_ids, list):
            answer_ids = [answer_ids]
        
        # Get question and validate answer IDs
        question = QuizQuestion.objects.get(id=question_id)
        valid_answer_ids = set(question.answers.values_list('id', flat=True))
        
        for answer_id in answer_ids:
            if int(answer_id) not in valid_answer_ids:
                return {
                    'valid': False,
                    'error': f'Invalid answer ID {answer_id} for question {question_id}'
                }
        
        # Validate answer count based on question type
        if question.question_type == QuizQuestion.QuestionType.SINGLE:
            if len(answer_ids) != 1:
                return {
                    'valid': False,
                    'error': f'Question {question_id} requires exactly one answer (single choice).'
                }
        elif question.question_type == QuizQuestion.QuestionType.TRUE_FALSE:
            if len(answer_ids) != 1:
                return {
                    'valid': False,
                    'error': f'Question {question_id} requires exactly one answer (true/false).'
                }
    
    return {
        'valid': True,
        'error': None
    }


def calculate_quiz_score(quiz: Quiz, answers: Dict) -> Dict:
    """
    Calculate score for a quiz submission.
    
    Args:
        quiz: Quiz instance
        answers: Dictionary mapping question IDs to answer ID lists
    
    Returns:
        Dictionary with scoring information
    """
    total_points = 0
    earned_points = 0
    results_by_question = {}
    
    for question in quiz.questions.all():
        question_id = str(question.id)
        total_points += question.points
        
        # Get user's answers
        user_answer_ids = answers.get(question_id, [])
        if not isinstance(user_answer_ids, list):
            user_answer_ids = [user_answer_ids]
        user_answer_ids = set(int(aid) for aid in user_answer_ids)
        
        # Get correct answer IDs
        correct_answer_ids = set(
            question.answers.filter(is_correct=True).values_list('id', flat=True)
        )
        
        # Calculate correctness
        is_correct = user_answer_ids == correct_answer_ids
        
        if is_correct:
            earned_points += question.points
        
        results_by_question[question.id] = {
            'correct': is_correct,
            'user_answers': list(user_answer_ids),
            'correct_answers': list(correct_answer_ids),
            'points_earned': question.points if is_correct else 0,
            'points_possible': question.points,
        }
    
    # Calculate percentage
    score_percentage = (earned_points / total_points * 100) if total_points > 0 else 0
    passed = score_percentage >= quiz.passing_score
    
    return {
        'score_percentage': score_percentage,
        'points_earned': earned_points,
        'total_points': total_points,
        'passed': passed,
        'results_by_question': results_by_question,
    }


def submit_quiz(
    quiz: Quiz,
    user,
    answers: Dict,
    session_token: str = None,
    request=None
) -> Dict:
    """
    Process a quiz submission with comprehensive validation and scoring.
    
    This function now requires a session token and performs extensive
    validation including:
    - Session token validation
    - Minimum time enforcement
    - Suspicious timing detection
    - Comprehensive audit logging
    
    Args:
        quiz: Quiz instance
        user: User submitting the quiz
        answers: Dictionary mapping question IDs to answer ID lists
        session_token: Session token for validation (required)
        request: HTTP request for IP/user agent tracking (optional)
    
    Returns:
        Dictionary with submission result or error
    """
    # Require session token for production security
    if not session_token:
        log_assessment_event(
            user=user,
            event_type=AssessmentAuditLog.EventType.VALIDATION_ERROR,
            severity=AssessmentAuditLog.Severity.ERROR,
            message="Quiz submission attempted without session token",
            quiz=quiz,
            request=request
        )
        return {
            'success': False,
            'error': 'Session token is required for quiz submission.'
        }
    
    # Validate session
    session_validation = validate_quiz_session(session_token, quiz, user, request)
    if not session_validation['valid']:
        log_assessment_event(
            user=user,
            event_type=AssessmentAuditLog.EventType.SUBMISSION_FAILED,
            severity=AssessmentAuditLog.Severity.ERROR,
            message=f"Session validation failed: {session_validation['error']}",
            quiz=quiz,
            request=request
        )
        return {
            'success': False,
            'error': session_validation['error']
        }
    
    session = session_validation['session']
    
    # Check for suspicious timing (minimum time + extremely fast detection)
    timing_check = detect_suspicious_timing(session, request)
    if timing_check['suspicious']:
        # Still reject if below minimum time
        if timing_check['time_taken'] < MINIMUM_QUIZ_TIME_SECONDS:
            return {
                'success': False,
                'error': f'Quiz submitted too quickly. Minimum {MINIMUM_QUIZ_TIME_SECONDS} seconds required. You took {timing_check["time_taken"]:.1f} seconds.'
            }
        # Flag but allow if just suspicious
        # (logged already in detect_suspicious_timing)
    
    # Validate submission data
    validation = validate_quiz_submission(quiz, user, answers)
    if not validation['valid']:
        log_assessment_event(
            user=user,
            event_type=AssessmentAuditLog.EventType.VALIDATION_ERROR,
            severity=AssessmentAuditLog.Severity.ERROR,
            message=f"Submission validation failed: {validation['error']}",
            quiz=quiz,
            session=session,
            request=request,
            metadata={'answers_count': len(answers)}
        )
        return {
            'success': False,
            'error': validation['error']
        }
    
    # Check time limit (session expiration already checked, but double check)
    if quiz.time_limit:
        elapsed_minutes = (timezone.now() - session.started_at).total_seconds() / 60
        if elapsed_minutes > quiz.time_limit:
            log_assessment_event(
                user=user,
                event_type=AssessmentAuditLog.EventType.TIME_LIMIT_EXCEEDED,
                severity=AssessmentAuditLog.Severity.WARNING,
                message=f"Time limit exceeded: {elapsed_minutes:.1f} minutes (limit: {quiz.time_limit})",
                quiz=quiz,
                session=session,
                request=request
            )
            session.deactivate()
            return {
                'success': False,
                'error': f'Time limit exceeded ({quiz.time_limit} minutes).'
            }
    
    # Calculate score
    scoring = calculate_quiz_score(quiz, answers)
    
    # Create or update attempt
    attempt, created = QuizAttempt.objects.get_or_create(
        user=user,
        quiz=quiz,
        submitted_at__isnull=True,
        defaults={
            'started_at': session.started_at
        }
    )
    
    # Calculate time taken
    time_taken = int((timezone.now() - session.started_at).total_seconds())
    
    # Update attempt with results
    attempt.score = scoring['score_percentage']
    attempt.points_earned = scoring['points_earned']
    attempt.total_points = scoring['total_points']
    attempt.passed = scoring['passed']
    attempt.submitted_at = timezone.now()
    attempt.time_taken = time_taken
    attempt.answers = {str(k): v for k, v in answers.items()}
    attempt.save()
    
    # Mark session as submitted
    session.submitted = True
    session.submitted_at = timezone.now()
    session.save(update_fields=['submitted', 'submitted_at'])
    session.deactivate()
    
    # Log successful submission
    log_assessment_event(
        user=user,
        event_type=AssessmentAuditLog.EventType.SUBMISSION_SUCCESS,
        severity=AssessmentAuditLog.Severity.INFO,
        message=f"Quiz submitted successfully: {scoring['score_percentage']:.1f}% ({'PASSED' if attempt.passed else 'FAILED'})",
        quiz=quiz,
        session=session,
        request=request,
        metadata={
            'score': scoring['score_percentage'],
            'passed': attempt.passed,
            'time_taken': time_taken,
            'attempt_number': attempt.get_attempt_number()
        }
    )
    
    return {
        'success': True,
        'attempt': attempt,
        'scoring': scoring,
        'attempt_number': attempt.get_attempt_number(),
        'attempts_remaining': max(0, quiz.max_attempts - attempt.get_attempt_number()),
        'time_taken': time_taken,
    }

