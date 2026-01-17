"""
Business logic for quiz submission and scoring.
"""
from typing import Dict, List
from django.utils import timezone
from .models import Quiz, QuizQuestion, QuizAnswer, QuizAttempt


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


def submit_quiz(quiz: Quiz, user, answers: Dict, started_at=None) -> Dict:
    """
    Process a quiz submission with validation and scoring.
    
    Args:
        quiz: Quiz instance
        user: User submitting the quiz
        answers: Dictionary mapping question IDs to answer ID lists
        started_at: Optional start time for time limit validation
    
    Returns:
        Dictionary with submission result or error
    """
    # Validate submission
    validation = validate_quiz_submission(quiz, user, answers)
    if not validation['valid']:
        return {
            'success': False,
            'error': validation['error']
        }
    
    # Check time limit if applicable
    if quiz.time_limit and started_at:
        elapsed_minutes = (timezone.now() - started_at).total_seconds() / 60
        if elapsed_minutes > quiz.time_limit:
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
            'started_at': started_at or timezone.now()
        }
    )
    
    # Calculate time taken
    time_taken = None
    if started_at:
        time_taken = int((timezone.now() - started_at).total_seconds())
    
    # Update attempt with results
    attempt.score = scoring['score_percentage']
    attempt.points_earned = scoring['points_earned']
    attempt.total_points = scoring['total_points']
    attempt.passed = scoring['passed']
    attempt.submitted_at = timezone.now()
    attempt.time_taken = time_taken
    attempt.answers = {str(k): v for k, v in answers.items()}
    attempt.save()
    
    return {
        'success': True,
        'attempt': attempt,
        'scoring': scoring,
        'attempt_number': attempt.get_attempt_number(),
        'attempts_remaining': max(0, quiz.max_attempts - attempt.get_attempt_number()),
    }
