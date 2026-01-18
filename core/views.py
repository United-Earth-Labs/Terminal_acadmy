"""
Core views for Terminal Academy.

These are the main template-based views for the web interface.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.urls import reverse_lazy

from users.forms import LoginForm, RegisterForm


def home(request):
    """Landing page for Terminal Academy."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


@login_required
def dashboard(request):
    """User dashboard showing progress and courses."""
    from progress.models import UserXP
    
    # Check if user is new (0 XP)
    user_xp = UserXP.objects.filter(user=request.user).first()
    is_new_user = not user_xp or user_xp.total_xp == 0
    
    context = {
        'user': request.user,
        'is_new_user': is_new_user,
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
    """Browse available courses with progress tracking (optimized)."""
    from courses.models import Course
    from progress.models import LessonProgress
    from django.db.models import Count, Q
    
    courses = Course.objects.filter(status='published').prefetch_related(
        'modules__lessons'
    ).order_by('level', 'title')
    
    # OPTIMIZATION: Get ALL progress for this user in ONE query
    # Build a dictionary mapping course_id -> completed_lesson_count
    user_progress = {}
    if courses.exists():
        course_ids = [course.id for course in courses]
        progress_data = LessonProgress.objects.filter(
            user=request.user,
            lesson__module__course_id__in=course_ids,
            completed=True
        ).values('lesson__module__course_id').annotate(
            completed_count=Count('id')
        )
        
        user_progress = {
            item['lesson__module__course_id']: item['completed_count']
            for item in progress_data
        }
    
    # Build course data with cached calculations
    courses_data = []
    for course in courses:
        # These use prefetched data (no additional queries)
        modules = course.modules.all()
        total_lessons = 0
        total_xp = 0
        total_duration = 0
        
        for module in modules:
            lessons = module.lessons.all()
            total_lessons += len(lessons)
            total_xp += sum(lesson.xp_reward for lesson in lessons)
            total_duration += sum(lesson.estimated_duration for lesson in lessons)
        
        # Get progress from our single query result
        completed_lessons = user_progress.get(course.id, 0)
        progress_percentage = round((completed_lessons / total_lessons * 100), 1) if total_lessons > 0 else 0
        
        courses_data.append({
            'course': course,
            'total_lessons': total_lessons,
            'total_xp': total_xp,
            'total_duration_hours': round(total_duration / 60, 1),
            'completed_lessons': completed_lessons,
            'progress_percentage': progress_percentage,
            'is_enrolled': completed_lessons > 0,
        })
    
    return render(request, 'courses.html', {'courses_data': courses_data})


@login_required
def labs_view(request):
    """Browse labs with filtering and search."""
    from labs.models import Lab, LabAttempt
    from courses.models import Course
    from django.db.models import Q
    
    # Start with active labs
    labs = Lab.objects.filter(is_active=True).select_related(
        'lesson__module__course', 'environment'
    )
    
    # Search query
    search_query = request.GET.get('q', '').strip()
    if search_query:
        labs = labs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(instructions__icontains=search_query)
        )
    
    # Difficulty filter
    difficulty = request.GET.get('difficulty', '')
    if difficulty and difficulty in ['easy', 'medium', 'hard', 'expert']:
        labs = labs.filter(difficulty=difficulty)
    
    # Course/category filter
    course_slug = request.GET.get('course', '')
    if course_slug:
        labs = labs.filter(lesson__module__course__slug=course_slug)
    
    # Sorting
    sort_by = request.GET.get('sort', 'newest')
    if sort_by == 'xp':
        labs = labs.order_by('-xp_reward')
    elif sort_by == 'difficulty':
        labs = labs.order_by('difficulty', 'title')
    elif sort_by == 'alphabetical':
        labs = labs.order_by('title')
    else:  # newest (default)
        labs = labs.order_by('-created_at')
    
    # Get completed labs
    completed_lab_ids = set()
    if request.user.is_authenticated:
        completed_lab_ids = set(
            LabAttempt.objects.filter(
                user=request.user,
                completed=True
            ).values_list('lab_id', flat=True)
        )
    
    # Get all courses for filter dropdown
    courses = Course.objects.filter(
        status='published',
        modules__lessons__labs__is_active=True
    ).distinct().order_by('title')
    
    context = {
        'labs': labs,
        'completed_lab_ids': completed_lab_ids,
        'courses': courses,
        'search_query': search_query,
        'selected_difficulty': difficulty,
        'selected_course': course_slug,
        'selected_sort': sort_by,
    }
    return render(request, 'labs.html', context)


@login_required
def course_detail_view(request, slug):
    """View course detail with progress tracking."""
    from django.shortcuts import get_object_or_404
    from courses.models import Course
    from progress.models import LessonProgress
    
    course = get_object_or_404(Course, slug=slug, status='published')
    modules = course.modules.prefetch_related('lessons').order_by('order')
    
    # Calculate total lessons and XP
    total_lessons = sum(module.lessons.count() for module in modules)
    total_xp = sum(
        lesson.xp_reward 
        for module in modules 
        for lesson in module.lessons.all()
    )
    total_duration = sum(
        lesson.estimated_duration 
        for module in modules 
        for lesson in module.lessons.all()
    )
    
    # Get user progress if authenticated
    completed_lesson_ids = set()
    completed_lessons = 0
    progress_percentage = 0
    
    if request.user.is_authenticated:
        completed_lesson_ids = set(
            LessonProgress.objects.filter(
                user=request.user,
                lesson__module__course=course,
                completed=True
            ).values_list('lesson_id', flat=True)
        )
        completed_lessons = len(completed_lesson_ids)
        progress_percentage = round((completed_lessons / total_lessons * 100), 1) if total_lessons > 0 else 0
    
    context = {
        'course': course,
        'modules': modules,
        'total_lessons': total_lessons,
        'total_xp': total_xp,
        'total_duration_hours': round(total_duration / 60, 1),
        'completed_lessons': completed_lessons,
        'progress_percentage': progress_percentage,
        'completed_lesson_ids': completed_lesson_ids,
        'is_enrolled': completed_lessons > 0,  # Consider enrolled if any lesson completed
    }
    return render(request, 'course_detail.html', context)


@login_required
@ensure_csrf_cookie
def lab_detail_view(request, lab_id):
    """View lab detail / terminal interface."""
    from django.shortcuts import get_object_or_404
    from labs.models import Lab
    from courses.models import Lesson
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
        
        # If no more lessons in this module, check next module
        if not next_lesson:
            from courses.models import Module
            next_module = Module.objects.filter(
                course=lab.lesson.module.course,
                order__gt=lab.lesson.module.order
            ).order_by('order').first()
            if next_module:
                next_lesson = next_module.lessons.order_by('order').first()
    
    return render(request, 'lab_terminal.html', {
        'lab': lab,
        'next_lesson': next_lesson,
        'course_slug': course_slug,
    })


@login_required
def achievements_view(request):
    """View achievements with progress tracking."""
    from progress.models import Achievement, UserAchievement
    from progress.utils import calculate_achievement_progress
    
    achievements = Achievement.objects.filter(is_hidden=False).order_by('category', 'xp_reward')
    
    # Get unlocked achievement IDs
    unlocked = set(
        UserAchievement.objects.filter(user=request.user).values_list('achievement_id', flat=True)
    )
    
    # Calculate progress for each achievement
    achievements_with_progress = []
    for achievement in achievements:
        progress = calculate_achievement_progress(request.user, achievement)
        achievements_with_progress.append({
            'achievement': achievement,
            'progress': progress
        })
    
    return render(request, 'achievements.html', {
        'achievements_data': achievements_with_progress,
        'unlocked': unlocked
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
