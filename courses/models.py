"""
Course and learning content models for Terminal Academy.

This module contains models for courses, modules, lessons, and
prerequisites that form the learning path structure.
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """Course category for organization."""
    
    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True, default='')
    icon = models.CharField(_('icon'), max_length=50, blank=True, default='')
    order = models.PositiveIntegerField(_('order'), default=0)
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Course(models.Model):
    """
    A course is the main learning unit containing multiple modules.
    
    Courses have skill level requirements and XP rewards.
    """
    
    class Level(models.TextChoices):
        BEGINNER = 'beginner', _('Beginner')
        INTERMEDIATE = 'intermediate', _('Intermediate')
        ADVANCED = 'advanced', _('Advanced')
        EXPERT = 'expert', _('Expert')
    
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        PUBLISHED = 'published', _('Published')
        ARCHIVED = 'archived', _('Archived')
    
    # Basic info
    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200, unique=True)
    description = models.TextField(_('description'))
    short_description = models.CharField(_('short description'), max_length=300, blank=True)
    
    # Categorization
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses'
    )
    level = models.CharField(
        _('level'),
        max_length=20,
        choices=Level.choices,
        default=Level.BEGINNER
    )
    
    # Media
    thumbnail = models.ImageField(
        _('thumbnail'),
        upload_to='courses/thumbnails/',
        null=True,
        blank=True
    )
    
    # Rewards
    xp_reward = models.PositiveIntegerField(_('XP reward'), default=100)
    estimated_duration = models.PositiveIntegerField(
        _('estimated duration (minutes)'),
        default=60
    )
    
    # Status
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    is_featured = models.BooleanField(_('is featured'), default=False)
    
    # Metadata
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_courses'
    )
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('course')
        verbose_name_plural = _('courses')
        ordering = ['level', 'title']
    
    def __str__(self):
        return self.title
    
    @property
    def module_count(self):
        return self.modules.count()
    
    @property
    def lesson_count(self):
        return sum(module.lessons.count() for module in self.modules.all())
    
    @property
    def lab_count(self):
        return sum(
            lesson.labs.count() 
            for module in self.modules.all() 
            for lesson in module.lessons.all()
        )


class CoursePrerequisite(models.Model):
    """
    Defines prerequisite courses that must be completed before
    starting a course.
    """
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='prerequisites'
    )
    prerequisite = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='required_for'
    )
    
    class Meta:
        verbose_name = _('course prerequisite')
        verbose_name_plural = _('course prerequisites')
        unique_together = ['course', 'prerequisite']
    
    def __str__(self):
        return f"{self.course.title} requires {self.prerequisite.title}"


class Module(models.Model):
    """
    A module is a section within a course containing related lessons.
    """
    
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='modules'
    )
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'), blank=True, default='')
    order = models.PositiveIntegerField(_('order'), default=0)
    
    # Unlock requirements
    requires_previous = models.BooleanField(
        _('requires previous module'),
        default=True,
        help_text=_('Whether completion of previous module is required')
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('module')
        verbose_name_plural = _('modules')
        ordering = ['order']
        unique_together = ['course', 'order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    
    @property
    def lesson_count(self):
        return self.lessons.count()


class Lesson(models.Model):
    """
    A lesson is an individual learning unit within a module.
    
    Lessons can contain text content, videos, and require labs.
    """
    
    class ContentType(models.TextChoices):
        TEXT = 'text', _('Text')
        VIDEO = 'video', _('Video')
        INTERACTIVE = 'interactive', _('Interactive')
        QUIZ = 'quiz', _('Quiz')
    
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
        related_name='lessons'
    )
    title = models.CharField(_('title'), max_length=200)
    slug = models.SlugField(_('slug'), max_length=200)
    
    # Content
    content_type = models.CharField(
        _('content type'),
        max_length=20,
        choices=ContentType.choices,
        default=ContentType.TEXT
    )
    content = models.TextField(_('content'))
    video_url = models.URLField(_('video URL'), blank=True, default='')
    
    # Ordering
    order = models.PositiveIntegerField(_('order'), default=0)
    
    # Requirements
    requires_lab_completion = models.BooleanField(
        _('requires lab completion'),
        default=False,
        help_text=_('Whether completing the lab is required to finish this lesson')
    )
    
    # Rewards
    xp_reward = models.PositiveIntegerField(_('XP reward'), default=10)
    estimated_duration = models.PositiveIntegerField(
        _('estimated duration (minutes)'),
        default=10
    )
    
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    
    class Meta:
        verbose_name = _('lesson')
        verbose_name_plural = _('lessons')
        ordering = ['order']
        unique_together = ['module', 'slug']
    
    def __str__(self):
        return f"{self.module.title} - {self.title}"


class LessonResource(models.Model):
    """
    Additional resources attached to a lesson (PDFs, links, etc.).
    """
    
    class ResourceType(models.TextChoices):
        PDF = 'pdf', _('PDF Document')
        LINK = 'link', _('External Link')
        CODE = 'code', _('Code Repository')
        TOOL = 'tool', _('Tool Reference')
    
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.CASCADE,
        related_name='resources'
    )
    title = models.CharField(_('title'), max_length=200)
    resource_type = models.CharField(
        _('resource type'),
        max_length=20,
        choices=ResourceType.choices
    )
    url = models.URLField(_('URL'), blank=True, default='')
    file = models.FileField(
        _('file'),
        upload_to='lessons/resources/',
        null=True,
        blank=True
    )
    description = models.TextField(_('description'), blank=True, default='')
    
    class Meta:
        verbose_name = _('lesson resource')
        verbose_name_plural = _('lesson resources')
    
    def __str__(self):
        return f"{self.lesson.title} - {self.title}"


class Quiz(models.Model):
    """Quiz attached to a lesson for assessment."""
    
    lesson = models.OneToOneField(
        Lesson,
        on_delete=models.CASCADE,
        related_name='quiz'
    )
    title = models.CharField(_('title'), max_length=200)
    passing_score = models.PositiveIntegerField(
        _('passing score percentage'),
        default=70
    )
    max_attempts = models.PositiveIntegerField(_('max attempts'), default=3)
    time_limit = models.PositiveIntegerField(
        _('time limit (minutes)'),
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = _('quiz')
        verbose_name_plural = _('quizzes')
    
    def __str__(self):
        return f"Quiz: {self.title}"


class QuizQuestion(models.Model):
    """Individual question within a quiz."""
    
    class QuestionType(models.TextChoices):
        SINGLE = 'single', _('Single Choice')
        MULTIPLE = 'multiple', _('Multiple Choice')
        TRUE_FALSE = 'true_false', _('True/False')
        TEXT = 'text', _('Text Answer')
    
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    question_text = models.TextField(_('question'))
    question_type = models.CharField(
        _('question type'),
        max_length=20,
        choices=QuestionType.choices,
        default=QuestionType.SINGLE
    )
    explanation = models.TextField(
        _('explanation'),
        blank=True,
        default='',
        help_text=_('Shown after answering')
    )
    order = models.PositiveIntegerField(_('order'), default=0)
    points = models.PositiveIntegerField(_('points'), default=1)
    
    class Meta:
        verbose_name = _('quiz question')
        verbose_name_plural = _('quiz questions')
        ordering = ['order']
    
    def __str__(self):
        return f"Q{self.order}: {self.question_text[:50]}"


class QuizAnswer(models.Model):
    """Answer option for a quiz question."""
    
    question = models.ForeignKey(
        QuizQuestion,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    answer_text = models.CharField(_('answer'), max_length=500)
    is_correct = models.BooleanField(_('is correct'), default=False)
    order = models.PositiveIntegerField(_('order'), default=0)
    
    class Meta:
        verbose_name = _('quiz answer')
        verbose_name_plural = _('quiz answers')
        ordering = ['order']
    
    def __str__(self):
        return f"{self.answer_text} ({'✓' if self.is_correct else '✗'})"


class QuizAttempt(models.Model):
    """Tracks user attempts at quizzes with scoring and validation."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='quiz_attempts'
    )
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name='attempts'
    )
    
    # Scoring
    score = models.FloatField(_('score percentage'), default=0)
    points_earned = models.PositiveIntegerField(_('points earned'), default=0)
    total_points = models.PositiveIntegerField(_('total points'), default=0)
    passed = models.BooleanField(_('passed'), default=False)
    
    # Timing
    started_at = models.DateTimeField(_('started at'), auto_now_add=True)
    submitted_at = models.DateTimeField(_('submitted at'), null=True, blank=True)
    time_taken = models.PositiveIntegerField(
        _('time taken (seconds)'),
        null=True,
        blank=True
    )
    
    # User answers stored as JSON: {question_id: [answer_id, ...]}
    answers = models.JSONField(_('answers'), default=dict)
    
    # XP tracking
    xp_awarded = models.BooleanField(_('XP awarded'), default=False)
    
    class Meta:
        verbose_name = _('quiz attempt')
        verbose_name_plural = _('quiz attempts')
        ordering = ['-started_at']
    
    def __str__(self):
        status = '✓' if self.passed else '✗'
        return f"{status} {self.user.email} - {self.quiz.title}: {self.score:.1f}%"
    
    @property
    def is_submitted(self):
        """Check if the attempt has been submitted."""
        return self.submitted_at is not None
    
    def get_attempt_number(self):
        """Get the attempt number for this user and quiz."""
        return QuizAttempt.objects.filter(
            user=self.user,
            quiz=self.quiz,
            started_at__lte=self.started_at
        ).count()

