"""
Core views for Terminal Acadmay.

These are the main template-based views for the web interface.
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.urls import reverse_lazy
from django.utils import timezone

from courses.models import Course, Lesson, Module, QuizAttempt
from courses.services import (
    MINIMUM_QUIZ_TIME_SECONDS,
    create_quiz_session,
    submit_quiz as submit_quiz_service,
)
from labs.models import Lab, LabAttempt
from progress.models import (
    LessonProgress,
    ModuleProgress,
    UserAchievement,
    UserProgress,
    UserXP,
)
from progress.services import award_xp, get_user_stats

from users.forms import LoginForm, RegisterForm


def _safe_get_quiz(lesson):
    try:
        return lesson.quiz
    except ObjectDoesNotExist:
        return None


def _get_course_lessons(course):
    return list(
        Lesson.objects.filter(module__course=course)
        .select_related('module')
        .order_by('module__order', 'order', 'id')
    )


def _get_adjacent_lessons(course, current_lesson):
    lessons = _get_course_lessons(course)
    for index, lesson in enumerate(lessons):
        if lesson.id != current_lesson.id:
            continue

        previous_lesson = lessons[index - 1] if index > 0 else None
        next_lesson = lessons[index + 1] if index + 1 < len(lessons) else None
        return previous_lesson, next_lesson

    return None, None


def _mark_lesson_started(user, lesson):
    UserProgress.objects.get_or_create(user=user, course=lesson.module.course)
    progress, _ = LessonProgress.objects.get_or_create(
        user=user,
        lesson=lesson,
        defaults={'started': True},
    )

    if not progress.started:
        progress.started = True
        progress.save(update_fields=['started'])

    return progress


def _sync_course_progress(user, course):
    total_lessons = Lesson.objects.filter(module__course=course).count()
    completed_lessons = LessonProgress.objects.filter(
        user=user,
        lesson__module__course=course,
        completed=True,
    ).count()
    percentage = int((completed_lessons / total_lessons) * 100) if total_lessons else 0

    user_progress, _ = UserProgress.objects.get_or_create(user=user, course=course)
    user_progress.percentage = percentage
    user_progress.completed_at = timezone.now() if percentage == 100 and total_lessons else None
    user_progress.save(update_fields=['percentage', 'completed_at', 'last_accessed'])

    for module in Module.objects.filter(course=course).prefetch_related('lessons'):
        total_module_lessons = module.lessons.count()
        completed_module_lessons = LessonProgress.objects.filter(
            user=user,
            lesson__module=module,
            completed=True,
        ).count()
        module_complete = total_module_lessons > 0 and completed_module_lessons == total_module_lessons

        module_progress, _ = ModuleProgress.objects.get_or_create(user=user, module=module)
        module_progress.completed = module_complete
        module_progress.completed_at = timezone.now() if module_complete else None
        module_progress.save(update_fields=['completed', 'completed_at'])

    return user_progress


def _complete_lesson(user, lesson):
    progress = _mark_lesson_started(user, lesson)
    xp_earned = 0

    if not progress.completed:
        progress.completed = True
        progress.completed_at = timezone.now()

    if not progress.xp_awarded:
        award_xp(user, lesson.xp_reward, f'Completed lesson: {lesson.title}')
        progress.xp_awarded = True
        xp_earned = lesson.xp_reward

    progress.save(update_fields=['started', 'completed', 'completed_at', 'xp_awarded'])
    course_progress = _sync_course_progress(user, lesson.module.course)
    return progress, xp_earned, course_progress


def _extract_takeaways(content, limit=4):
    takeaways = []
    for raw_line in content.splitlines():
        line = raw_line.strip().lstrip('-*#0123456789. ')
        if len(line) < 12:
            continue
        if line in takeaways:
            continue
        takeaways.append(line)
        if len(takeaways) == limit:
            break

    if not takeaways and content.strip():
        takeaways.append(content.strip()[:180])

    return takeaways


def _get_next_lesson_for_user(user, course):
    lessons = _get_course_lessons(course)
    completed_ids = set(
        LessonProgress.objects.filter(
            user=user,
            lesson__module__course=course,
            completed=True,
        ).values_list('lesson_id', flat=True)
    )

    for lesson in lessons:
        if lesson.id not in completed_ids:
            return lesson

    return lessons[-1] if lessons else None


def _get_lesson_page_context(user, course, lesson):
    lesson_progress = _mark_lesson_started(user, lesson)
    previous_lesson, next_lesson = _get_adjacent_lessons(course, lesson)
    lab = lesson.labs.order_by('id').first()
    lab_attempt = None
    lab_completed = not lesson.requires_lab_completion
    if lab:
        lab_attempt = LabAttempt.objects.filter(user=user, lab=lab).first()
        if lesson.requires_lab_completion:
            lab_completed = bool(lab_attempt and lab_attempt.completed)

    quiz = _safe_get_quiz(lesson)
    latest_quiz_attempt = None
    attempts_count = 0
    if quiz:
        latest_quiz_attempt = QuizAttempt.objects.filter(
            user=user,
            quiz=quiz,
            submitted_at__isnull=False,
        ).order_by('-submitted_at').first()
        attempts_count = QuizAttempt.objects.filter(
            user=user,
            quiz=quiz,
            submitted_at__isnull=False,
        ).count()

    course_progress = _sync_course_progress(user, course)
    return {
        'lesson_progress': lesson_progress,
        'previous_lesson': previous_lesson,
        'next_lesson': next_lesson,
        'lab': lab,
        'lab_attempt': lab_attempt,
        'lab_completed': lab_completed,
        'quiz': quiz,
        'latest_quiz_attempt': latest_quiz_attempt,
        'quiz_attempts_count': attempts_count,
        'course_progress': course_progress,
        'takeaways': _extract_takeaways(lesson.content),
    }


def home(request):
    """Landing page for Terminal Acadmay."""
    if request.user.is_authenticated:
        return redirect('dashboard')

    featured_courses = list(
        Course.objects.filter(status='published', is_featured=True)
        .prefetch_related('modules__lessons')
        .order_by('level', 'title')[:3]
    )
    if len(featured_courses) < 3:
        fallback_courses = Course.objects.filter(status='published').prefetch_related('modules__lessons').order_by('level', 'title')[:3]
        featured_courses = list(fallback_courses)

    context = {
        'featured_courses': featured_courses,
        'platform_stats': {
            'courses': Course.objects.filter(status='published').count(),
            'lessons': Lesson.objects.filter(module__course__status='published').count(),
            'labs': Lab.objects.filter(is_active=True).count(),
        },
    }
    return render(request, 'home.html', context)


@login_required
def dashboard(request):
    """User dashboard showing progress and courses."""
    active_progress = list(
        UserProgress.objects.filter(user=request.user)
        .select_related('course')
        .order_by('-last_accessed')
    )
    for progress in active_progress:
        progress.next_lesson = _get_next_lesson_for_user(request.user, progress.course)

    level_map = {
        'not_assessed': 'beginner',
        'beginner': 'beginner',
        'intermediate': 'intermediate',
        'advanced': 'advanced',
        'expert': 'expert',
    }
    started_course_ids = [progress.course_id for progress in active_progress]
    recommended_courses = list(
        Course.objects.filter(
            status='published',
            level=level_map.get(request.user.skill_level, 'beginner'),
        )
        .exclude(id__in=started_course_ids)
        .prefetch_related('modules__lessons')[:3]
    )
    recent_achievements = UserAchievement.objects.filter(user=request.user).select_related('achievement').order_by('-unlocked_at')[:4]
    leaderboard_preview = UserXP.objects.select_related('user').order_by('-total_xp')[:5]

    context = {
        'user': request.user,
        'stats': get_user_stats(request.user),
        'continue_learning': active_progress[:3],
        'primary_progress': active_progress[0] if active_progress else None,
        'recommended_courses': recommended_courses,
        'recent_achievements': recent_achievements,
        'leaderboard_preview': leaderboard_preview,
    }
    return render(request, 'dashboard.html', context)


@require_http_methods(['GET', 'POST'])
def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, 'Welcome back!')
                
                # Check if user needs to accept ethical agreement
                if not user.ethical_agreement_accepted:
                    return redirect('ethical_agreement')
                
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid email or password.')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def register_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Specify backend since we have multiple auth backends
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Welcome to Terminal Academy!')
            return redirect('ethical_agreement')
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})


@login_required
def logout_view(request):
    """User logout view."""
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
@require_http_methods(['GET', 'POST'])
def ethical_agreement(request):
    """Ethical hacking agreement acceptance view."""
    if request.user.ethical_agreement_accepted:
        return redirect('dashboard')
    
    if request.method == 'POST':
        if request.POST.get('agree') == 'yes':
            request.user.ethical_agreement_accepted = True
            request.user.save()
            messages.success(request, 'Thank you for accepting the ethical agreement.')
            return redirect('skill_assessment')
        else:
            messages.error(request, 'You must accept the ethical agreement to continue.')
    
    return render(request, 'ethical_agreement.html')


@login_required
@require_http_methods(['GET', 'POST'])
def skill_assessment(request):
    """Skill assessment view to determine user level."""
    # Check if user already completed assessment
    if request.user.skill_assessment_completed_at:
        messages.warning(request, 'You have already completed the skill assessment.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        # Process skill assessment answers
        from users.services import process_skill_assessment
        result = process_skill_assessment(request.POST)
        
        if not result['success']:
            messages.error(request, result['error'])
            return render(request, 'skill_assessment.html')
        
        # Save results
        from django.utils import timezone
        request.user.skill_level = result['skill_level']
        request.user.skill_assessment_completed_at = timezone.now()
        request.user.save(update_fields=['skill_level', 'skill_assessment_completed_at'])
        
        messages.success(
            request, 
            f'Assessment complete! Your skill level: {result["skill_level"]} '
            f'(Score: {result["score"]}/{result["total"]})'
        )
        return redirect('dashboard')
    
    return render(request, 'skill_assessment.html')


@login_required
def courses_view(request):
    """Browse available courses."""
    courses = list(
        Course.objects.filter(status='published')
        .prefetch_related('modules__lessons')
        .order_by('level', 'title')
    )
    progress_map = {
        progress.course_id: progress
        for progress in UserProgress.objects.filter(user=request.user, course__in=courses)
    }
    for course in courses:
        course.progress_info = progress_map.get(course.id)
        course.next_lesson = _get_next_lesson_for_user(request.user, course)
    return render(request, 'courses.html', {'courses': courses})


@login_required
def labs_view(request):
    """Browse available labs."""
    from labs.models import Lab, LabAttempt
    labs = Lab.objects.filter(is_active=True).order_by('difficulty', 'title')
    completed_lab_ids = LabAttempt.objects.filter(
        user=request.user, completed=True
    ).values_list('lab_id', flat=True)
    return render(request, 'labs.html', {
        'labs': labs,
        'completed_lab_ids': list(completed_lab_ids),
    })


@login_required
def course_detail_view(request, slug):
    """View course detail."""
    course = get_object_or_404(
        Course.objects.prefetch_related('modules__lessons__labs', 'modules__lessons__quiz'),
        slug=slug,
        status='published',
    )
    modules = list(course.modules.order_by('order'))
    lesson_progress_map = {
        progress.lesson_id: progress
        for progress in LessonProgress.objects.filter(
            user=request.user,
            lesson__module__course=course,
        )
    }
    completed_lab_lesson_ids = set(
        LabAttempt.objects.filter(
            user=request.user,
            lab__lesson__module__course=course,
            completed=True,
        ).values_list('lab__lesson_id', flat=True)
    )
    passed_quiz_lesson_ids = set(
        QuizAttempt.objects.filter(
            user=request.user,
            quiz__lesson__module__course=course,
            passed=True,
            submitted_at__isnull=False,
        ).values_list('quiz__lesson_id', flat=True)
    )

    ordered_lessons = []
    for module in modules:
        module.lesson_items = list(module.lessons.order_by('order'))
        ordered_lessons.extend(module.lesson_items)

    completed_ids = {
        lesson_id
        for lesson_id, progress in lesson_progress_map.items()
        if progress.completed
    }
    unlocked = True
    current_lesson = None
    for index, lesson in enumerate(ordered_lessons, start=1):
        lesson.sequence_number = index
        lesson.progress_info = lesson_progress_map.get(lesson.id)
        lesson.lab = lesson.labs.order_by('id').first()
        lesson.quiz_object = _safe_get_quiz(lesson)
        lesson.lab_completed = lesson.id in completed_lab_lesson_ids
        lesson.quiz_completed = lesson.id in passed_quiz_lesson_ids
        lesson.is_completed = lesson.id in completed_ids
        lesson.is_available = unlocked or lesson.is_completed
        lesson.status_label = 'Completed' if lesson.is_completed else ('Continue' if lesson.progress_info else 'Start')
        if current_lesson is None and not lesson.is_completed:
            current_lesson = lesson
        if not lesson.is_completed and unlocked:
            unlocked = False

    if current_lesson is None and ordered_lessons:
        current_lesson = ordered_lessons[-1]

    course_progress = UserProgress.objects.filter(user=request.user, course=course).first()
    if course_progress:
        course_progress = _sync_course_progress(request.user, course)

    return render(request, 'course_detail.html', {
        'course': course,
        'modules': modules,
        'current_lesson': current_lesson,
        'course_progress': course_progress,
        'completed_lessons': len(completed_ids),
        'total_lessons': len(ordered_lessons),
    })


@login_required
@require_http_methods(['GET', 'POST'])
def lesson_detail_view(request, slug, lesson_slug):
    """Render the lesson page and handle completion for lesson-only flows."""
    course = get_object_or_404(Course, slug=slug, status='published')
    lesson = get_object_or_404(
        Lesson.objects.select_related('module').prefetch_related('resources', 'labs'),
        slug=lesson_slug,
        module__course=course,
    )

    page_context = _get_lesson_page_context(request.user, course, lesson)
    quiz = page_context['quiz']

    if request.method == 'POST' and request.POST.get('action') == 'complete_lesson':
        if lesson.requires_lab_completion and not page_context['lab_completed']:
            messages.error(request, 'Complete the lesson lab before finishing this lesson.')
        elif quiz:
            return redirect('lesson_quiz', slug=course.slug, lesson_slug=lesson.slug)
        else:
            _, lesson_xp, _ = _complete_lesson(request.user, lesson)
            request.session['lesson_summary_flash'] = {
                'lesson_xp': lesson_xp,
                'quiz_xp': 0,
            }
            messages.success(request, 'Lesson completed. Review the summary before moving on.')
            return redirect('lesson_summary', slug=course.slug, lesson_slug=lesson.slug)

    context = {
        'course': course,
        'lesson': lesson,
        **page_context,
    }
    return render(request, 'lesson_detail.html', context)


@login_required
@require_http_methods(['GET', 'POST'])
def lesson_quiz_view(request, slug, lesson_slug):
    """Render and submit the lesson quiz experience."""
    course = get_object_or_404(Course, slug=slug, status='published')
    lesson = get_object_or_404(
        Lesson.objects.select_related('module').prefetch_related('quiz__questions__answers'),
        slug=lesson_slug,
        module__course=course,
    )
    page_context = _get_lesson_page_context(request.user, course, lesson)
    quiz = page_context['quiz']

    if not quiz:
        messages.info(request, 'This lesson does not have a quiz yet.')
        return redirect('lesson_detail', slug=course.slug, lesson_slug=lesson.slug)

    if lesson.requires_lab_completion and not page_context['lab_completed']:
        messages.error(request, 'Complete the lesson lab before taking the quiz.')
        return redirect('lesson_detail', slug=course.slug, lesson_slug=lesson.slug)

    latest_pass = QuizAttempt.objects.filter(
        user=request.user,
        quiz=quiz,
        passed=True,
        submitted_at__isnull=False,
    ).order_by('-submitted_at').first()
    if latest_pass and page_context['lesson_progress'].completed:
        return redirect('lesson_summary', slug=course.slug, lesson_slug=lesson.slug)

    latest_result = None
    feedback_questions = []
    attempts_count = QuizAttempt.objects.filter(
        user=request.user,
        quiz=quiz,
        submitted_at__isnull=False,
    ).count()
    attempts_remaining = max(0, quiz.max_attempts - attempts_count)

    if request.method == 'POST':
        answers = {}
        for question in quiz.questions.all().order_by('order'):
            field_name = f'question_{question.id}'
            raw_answers = request.POST.getlist(field_name)
            answers[str(question.id)] = [int(answer_id) for answer_id in raw_answers if answer_id]

        submission = submit_quiz_service(
            quiz=quiz,
            user=request.user,
            answers=answers,
            session_token=request.POST.get('session_token'),
            request=request,
        )

        if not submission['success']:
            messages.error(request, submission['error'])
        else:
            latest_result = submission
            attempt = submission['attempt']
            quiz_xp = 0
            if attempt.passed and not attempt.xp_awarded:
                award_xp(request.user, lesson.xp_reward, f'Passed quiz: {quiz.title}')
                attempt.xp_awarded = True
                attempt.save(update_fields=['xp_awarded'])
                quiz_xp = lesson.xp_reward

            if attempt.passed:
                _, lesson_xp, _ = _complete_lesson(request.user, lesson)
                request.session['lesson_summary_flash'] = {
                    'lesson_xp': lesson_xp,
                    'quiz_xp': quiz_xp,
                }
                messages.success(request, 'Quiz passed. Your lesson summary is ready.')
                return redirect('lesson_summary', slug=course.slug, lesson_slug=lesson.slug)

            messages.error(request, 'Quiz submitted, but you did not reach the passing score yet.')
            attempts_count = QuizAttempt.objects.filter(
                user=request.user,
                quiz=quiz,
                submitted_at__isnull=False,
            ).count()
            attempts_remaining = max(0, quiz.max_attempts - attempts_count)

    if latest_result:
        for question in quiz.questions.all().order_by('order'):
            result = latest_result['scoring']['results_by_question'][question.id]
            question.selected_answer_ids = set(result['user_answers'])
            question.correct_answer_ids = set(result['correct_answers'])
            question.was_correct = result['correct']
            feedback_questions.append(question)
    else:
        feedback_questions = list(quiz.questions.all().order_by('order'))
        for question in feedback_questions:
            question.selected_answer_ids = set()
            question.correct_answer_ids = set()

    session_info = None
    if attempts_remaining > 0:
        session_info = create_quiz_session(quiz, request.user, request)

    context = {
        'course': course,
        'lesson': lesson,
        'quiz': quiz,
        'questions': feedback_questions,
        'session_info': session_info,
        'attempts_count': attempts_count,
        'attempts_remaining': attempts_remaining,
        'latest_result': latest_result,
        'minimum_quiz_seconds': MINIMUM_QUIZ_TIME_SECONDS,
        **page_context,
    }
    return render(request, 'lesson_quiz.html', context)


@login_required
def lesson_summary_view(request, slug, lesson_slug):
    """Render the post-lesson summary page."""
    course = get_object_or_404(Course, slug=slug, status='published')
    lesson = get_object_or_404(
        Lesson.objects.select_related('module').prefetch_related('resources', 'labs'),
        slug=lesson_slug,
        module__course=course,
    )
    page_context = _get_lesson_page_context(request.user, course, lesson)
    if not page_context['lesson_progress'].completed:
        messages.info(request, 'Complete the lesson before viewing its summary.')
        return redirect('lesson_detail', slug=course.slug, lesson_slug=lesson.slug)

    summary_flash = request.session.pop('lesson_summary_flash', None)
    latest_quiz_attempt = page_context['latest_quiz_attempt']
    course_progress = _sync_course_progress(request.user, course)
    is_course_complete = course_progress.percentage == 100

    context = {
        'course': course,
        'lesson': lesson,
        'summary_flash': summary_flash,
        'is_course_complete': is_course_complete,
        **page_context,
    }
    return render(request, 'lesson_summary.html', context)


@login_required
@ensure_csrf_cookie
def lab_detail_view(request, lab_id):
    """View lab detail / terminal interface."""
    lab = get_object_or_404(Lab, id=lab_id, is_active=True)
    
    # Find next lesson in the course for auto-navigation after completion
    next_lesson = None
    course_slug = None
    if lab.lesson and lab.lesson.module:
        course_slug = lab.lesson.module.course.slug
        next_lesson = Lesson.objects.filter(
            module=lab.lesson.module,
            order__gt=lab.lesson.order
        ).order_by('order').first()
        
        _mark_lesson_started(request.user, lab.lesson)

        # If no more lessons in this module, check next module
        if not next_lesson:
            next_module = Module.objects.filter(
                course=lab.lesson.module.course,
                order__gt=lab.lesson.module.order
            ).order_by('order').first()
            if next_module:
                next_lesson = next_module.lessons.order_by('order').first()
    
    # If this is a React course, use the interactive frontend lab template
    template_name = 'lab_terminal.html'
    if course_slug == 'react-zero-to-hero':
        template_name = 'lab_react.html'
    
    return render(request, template_name, {
        'lab': lab,
        'next_lesson': next_lesson,
        'course_slug': course_slug,
    })


@login_required
def achievements_view(request):
    """View user achievements."""
    from progress.models import Achievement, UserAchievement
    all_achievements = Achievement.objects.filter(is_hidden=False)
    user_achievements = UserAchievement.objects.filter(user=request.user).values_list('achievement_id', flat=True)
    return render(request, 'achievements.html', {
        'achievements': all_achievements,
        'unlocked': list(user_achievements),
    })


@login_required
def profile_view(request):
    """User profile page."""
    return render(request, 'profile.html', {'user': request.user})


@login_required
def leaderboard_view(request):
    """Global leaderboard."""
    from progress.models import UserXP
    top_users = UserXP.objects.select_related('user').order_by('-total_xp')[:50]
    return render(request, 'leaderboard.html', {'top_users': top_users})


# Legal pages (public - no login required)
def privacy_view(request):
    """Privacy Policy page."""
    return render(request, 'privacy.html')


def terms_view(request):
    """Terms of Service page."""
    return render(request, 'terms.html')


def about_view(request):
    """About Us page."""
    return render(request, 'about.html')


def contact_view(request):
    """Contact page."""
    return render(request, 'contact.html')


# Password Reset Views (using Django's built-in class-based views)
class CustomPasswordResetView(PasswordResetView):
    """Password reset request view."""
    template_name = 'password_reset_form.html'
    email_template_name = 'password_reset_email.html'
    subject_template_name = 'password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    """Password reset email sent confirmation."""
    template_name = 'password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    """Password reset confirmation view (from email link)."""
    template_name = 'password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    """Password reset complete view."""
    template_name = 'password_reset_complete.html'


# Wrap class-based views as functions for URL patterns
password_reset_request = CustomPasswordResetView.as_view()
password_reset_done = CustomPasswordResetDoneView.as_view()
password_reset_confirm = CustomPasswordResetConfirmView.as_view()
password_reset_complete = CustomPasswordResetCompleteView.as_view()
