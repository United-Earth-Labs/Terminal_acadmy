"""
API views for courses.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from .models import Category, Course, Module, Lesson, Quiz, QuizAttempt
from .serializers import (
    CategorySerializer, CourseListSerializer, CourseDetailSerializer,
    ModuleDetailSerializer, LessonDetailSerializer
)
from users.permissions import HasAcceptedEthicalAgreement


@api_view(['GET'])
@permission_classes([AllowAny])
def category_list(request):
    """List all course categories."""
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def course_list(request):
    """List all published courses with optional filtering."""
    courses = Course.objects.filter(status='published').select_related('category')
    
    # Filter by category
    category_slug = request.query_params.get('category')
    if category_slug:
        courses = courses.filter(category__slug=category_slug)
    
    # Filter by level
    level = request.query_params.get('level')
    if level:
        courses = courses.filter(level=level)
    
    # Filter featured
    featured = request.query_params.get('featured')
    if featured == 'true':
        courses = courses.filter(is_featured=True)
    
    serializer = CourseListSerializer(courses, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def course_detail(request, slug):
    """Get full course details."""
    course = get_object_or_404(
        Course.objects.prefetch_related(
            'modules__lessons__resources',
            'prerequisites__prerequisite'
        ),
        slug=slug,
        status='published'
    )
    serializer = CourseDetailSerializer(course)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, HasAcceptedEthicalAgreement])
def module_detail(request, course_slug, module_id):
    """Get module details with lessons."""
    course = get_object_or_404(Course, slug=course_slug, status='published')
    module = get_object_or_404(
        Module.objects.prefetch_related('lessons'),
        id=module_id,
        course=course
    )
    
    # Check if user can access this module
    if module.requires_previous and module.order > 1:
        # Check if previous module is completed
        previous_module = Module.objects.filter(
            course=course,
            order=module.order - 1
        ).first()
        
        if previous_module:
            from progress.models import ModuleProgress
            progress = ModuleProgress.objects.filter(
                user=request.user,
                module=previous_module,
                completed=True
            ).exists()
            
            if not progress:
                return Response(
                    {'error': 'You must complete the previous module first.'},
                    status=status.HTTP_403_FORBIDDEN
                )
    
    serializer = ModuleDetailSerializer(module)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated, HasAcceptedEthicalAgreement])
def lesson_detail(request, course_slug, lesson_slug):
    """Get lesson content."""
    course = get_object_or_404(Course, slug=course_slug, status='published')
    lesson = get_object_or_404(
        Lesson.objects.select_related('module', 'quiz').prefetch_related(
            'resources', 'quiz__questions__answers'
        ),
        slug=lesson_slug,
        module__course=course
    )
    
    # Mark lesson as started for progress tracking
    from progress.models import LessonProgress
    LessonProgress.objects.get_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'started': True}
    )
    
    serializer = LessonDetailSerializer(lesson)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, HasAcceptedEthicalAgreement])
def complete_lesson(request, course_slug, lesson_slug):
    """Mark a lesson as completed."""
    course = get_object_or_404(Course, slug=course_slug, status='published')
    lesson = get_object_or_404(
        Lesson,
        slug=lesson_slug,
        module__course=course
    )
    
    # Check if lab completion is required
    if lesson.requires_lab_completion:
        from labs.models import LabAttempt
        lab_completed = LabAttempt.objects.filter(
            user=request.user,
            lab__lesson=lesson,
            completed=True
        ).exists()
        
        if not lab_completed:
            return Response(
                {'error': 'You must complete the lab before completing this lesson.'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Mark lesson as completed
    from progress.models import LessonProgress
    progress, created = LessonProgress.objects.update_or_create(
        user=request.user,
        lesson=lesson,
        defaults={'completed': True}
    )
    
    # Award XP
    if created or not progress.xp_awarded:
        from progress.services import award_xp
        award_xp(request.user, lesson.xp_reward, f'Completed lesson: {lesson.title}')
        progress.xp_awarded = True
        progress.save()
    
    return Response({
        'message': 'Lesson completed!',
        'xp_earned': lesson.xp_reward if created else 0,
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommended_courses(request):
    """Get recommended courses based on user skill level."""
    user = request.user
    
    # Get courses matching user's skill level
    level_map = {
        'not_assessed': 'beginner',
        'beginner': 'beginner',
        'intermediate': 'intermediate',
        'advanced': 'advanced',
        'expert': 'expert',
    }
    
    target_level = level_map.get(user.skill_level, 'beginner')
    
    # Get courses user hasn't started
    from progress.models import UserProgress
    started_course_ids = UserProgress.objects.filter(
        user=user
    ).values_list('course_id', flat=True)
    
    courses = Course.objects.filter(
        status='published',
        level=target_level
    ).exclude(
        id__in=started_course_ids
    ).select_related('category')[:5]
    
    serializer = CourseListSerializer(courses, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, HasAcceptedEthicalAgreement])
def submit_quiz(request, quiz_id):
    """Submit quiz answers and get results."""
    quiz = get_object_or_404(
        Quiz.objects.prefetch_related('questions__answers'),
        id=quiz_id
    )
    
    # Get answers from request
    answers = request.data.get('answers', {})
    started_at_str = request.data.get('started_at')
    
    # Parse start time if provided
    started_at = None
    if started_at_str:
        started_at = parse_datetime(started_at_str)
        if not started_at:
            # Try as timestamp
            try:
                from datetime import datetime
                started_at = datetime.fromtimestamp(float(started_at_str), tz=timezone.utc)
            except (ValueError, TypeError):
                pass
    
    # Submit quiz using service
    from .services import submit_quiz as submit_quiz_service
    result = submit_quiz_service(quiz, request.user, answers, started_at)
    
    if not result['success']:
        return Response(
            {'error': result['error']},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    attempt = result['attempt']
    scoring = result['scoring']
    
    # Award XP if passed and first time passing
    if attempt.passed and not attempt.xp_awarded:
        # Get lesson XP reward
        lesson = quiz.lesson
        from progress.services import award_xp
        award_xp(request.user, lesson.xp_reward, f'Passed quiz: {quiz.title}')
        attempt.xp_awarded = True
        attempt.save(update_fields=['xp_awarded'])
    
    return Response({
        'success': True,
        'passed': attempt.passed,
        'score': attempt.score,
        'points_earned': attempt.points_earned,
        'total_points': attempt.total_points,
        'attempt_number': result['attempt_number'],
        'attempts_remaining': result['attempts_remaining'],
        'time_taken': attempt.time_taken,
        'xp_awarded': lesson.xp_reward if (attempt.passed and attempt.xp_awarded) else 0,
        'results': scoring['results_by_question'],
    })

