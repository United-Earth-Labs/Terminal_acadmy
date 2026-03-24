"""
Progress and achievement models for Terminal Academy.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class UserProgress(models.Model):
    """
    Tracks a user's progress through a course.
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='course_progress'
    )
    course = models.ForeignKey(
        'courses.Course',
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    
    # Progress percentage
    percentage = models.PositiveIntegerField(_('percentage'), default=0)
    
    # Timestamps
    started_at = models.DateTimeField(_('started at'), auto_now_add=True)
    last_accessed = models.DateTimeField(_('last accessed'), auto_now=True)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('user progress')
        verbose_name_plural = _('user progress')
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.email} - {self.course.title}: {self.percentage}%"


class ModuleProgress(models.Model):
    """
    Tracks a user's progress through a module.
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='module_progress'
    )
    module = models.ForeignKey(
        'courses.Module',
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    
    completed = models.BooleanField(_('completed'), default=False)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('module progress')
        verbose_name_plural = _('module progress')
        unique_together = ['user', 'module']
    
    def __str__(self):
        status = '✓' if self.completed else '○'
        return f"{status} {self.user.email} - {self.module.title}"


class LessonProgress(models.Model):
    """
    Tracks a user's progress through a lesson.
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lesson_progress'
    )
    lesson = models.ForeignKey(
        'courses.Lesson',
        on_delete=models.CASCADE,
        related_name='user_progress'
    )
    
    started = models.BooleanField(_('started'), default=False)
    completed = models.BooleanField(_('completed'), default=False)
    completed_at = models.DateTimeField(_('completed at'), null=True, blank=True)
    
    xp_awarded = models.BooleanField(_('XP awarded'), default=False)
    
    class Meta:
        verbose_name = _('lesson progress')
        verbose_name_plural = _('lesson progress')
        unique_together = ['user', 'lesson']
    
    def __str__(self):
        status = '✓' if self.completed else ('○' if self.started else '·')
        return f"{status} {self.user.email} - {self.lesson.title}"


class UserXP(models.Model):
    """
    Tracks a user's total XP and level.
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='xp'
    )
    
    total_xp = models.PositiveIntegerField(_('total XP'), default=0)
    level = models.PositiveIntegerField(_('level'), default=1)
    
    class Meta:
        verbose_name = _('user XP')
        verbose_name_plural = _('user XP')
    
    def __str__(self):
        return f"{self.user.email}: Level {self.level} ({self.total_xp} XP)"
    
    @property
    def xp_for_next_level(self):
        """Calculate XP needed to reach next level."""
        return self.level * 100
    
    @property
    def xp_progress(self):
        """Get progress towards next level as percentage."""
        current_level_xp = sum(i * 100 for i in range(1, self.level))
        xp_in_current_level = self.total_xp - current_level_xp
        return min(100, int(xp_in_current_level / self.xp_for_next_level * 100))


class XPTransaction(models.Model):
    """
    Log of XP transactions for auditing and history.
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='xp_transactions'
    )
    
    amount = models.IntegerField(_('amount'))
    reason = models.CharField(_('reason'), max_length=200)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('XP transaction')
        verbose_name_plural = _('XP transactions')
        ordering = ['-created_at']
    
    def __str__(self):
        sign = '+' if self.amount > 0 else ''
        return f"{self.user.email}: {sign}{self.amount} XP - {self.reason}"


class Achievement(models.Model):
    """
    Achievements that users can unlock.
    """
    
    class Category(models.TextChoices):
        PROGRESS = 'progress', _('Progress')
        SKILL = 'skill', _('Skill')
        CHALLENGE = 'challenge', _('Challenge')
        SPECIAL = 'special', _('Special')
    
    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    description = models.TextField(_('description'))
    
    category = models.CharField(
        _('category'),
        max_length=20,
        choices=Category.choices,
        default=Category.PROGRESS
    )
    
    # Requirements (JSON)
    requirements = models.JSONField(
        _('requirements'),
        default=dict,
        help_text=_('Conditions to unlock this achievement')
    )
    
    # Rewards
    xp_reward = models.PositiveIntegerField(_('XP reward'), default=50)
    badge_image = models.ImageField(
        _('badge image'),
        upload_to='achievements/',
        null=True,
        blank=True
    )
    
    # Rarity
    is_hidden = models.BooleanField(_('is hidden'), default=False)
    is_rare = models.BooleanField(_('is rare'), default=False)
    
    class Meta:
        verbose_name = _('achievement')
        verbose_name_plural = _('achievements')
    
    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    """
    Achievements unlocked by users.
    """
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='achievements'
    )
    achievement = models.ForeignKey(
        Achievement,
        on_delete=models.CASCADE,
        related_name='users'
    )
    
    unlocked_at = models.DateTimeField(_('unlocked at'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('user achievement')
        verbose_name_plural = _('user achievements')
        unique_together = ['user', 'achievement']
    
    def __str__(self):
        return f"{self.user.email} unlocked {self.achievement.name}"


class Streak(models.Model):
    """
    Tracks user's daily learning streaks.
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='streak'
    )
    
    current_streak = models.PositiveIntegerField(_('current streak'), default=0)
    longest_streak = models.PositiveIntegerField(_('longest streak'), default=0)
    last_activity_date = models.DateField(_('last activity date'), null=True, blank=True)
    
    class Meta:
        verbose_name = _('streak')
        verbose_name_plural = _('streaks')
    
    def __str__(self):
        return f"{self.user.email}: {self.current_streak} day streak"
