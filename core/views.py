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

from users.forms import LoginForm, RegisterForm


def home(request):
    """Landing page for Terminal Academy."""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'home.html')


@login_required
def dashboard(request):
    """User dashboard showing progress and courses."""
    context = {
        'user': request.user,
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
    from courses.models import Course
    courses = Course.objects.filter(status='published').order_by('title')
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
    from django.shortcuts import get_object_or_404
    from courses.models import Course
    course = get_object_or_404(Course, slug=slug, status='published')
    modules = course.modules.prefetch_related('lessons').order_by('order')
    return render(request, 'course_detail.html', {
        'course': course,
        'modules': modules,
    })


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

