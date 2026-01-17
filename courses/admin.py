"""
Admin configuration for Course models.
"""
from django.contrib import admin
from .models import (
    Category, Course, CoursePrerequisite, Module, 
    Lesson, LessonResource, Quiz, QuizQuestion, QuizAnswer,
    QuizAttempt, AssessmentSession, AssessmentAuditLog
)


class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    ordering = ['order']


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    ordering = ['order']


class QuizQuestionInline(admin.TabularInline):
    model = QuizQuestion
    extra = 1
    ordering = ['order']


class QuizAnswerInline(admin.TabularInline):
    model = QuizAnswer
    extra = 2
    ordering = ['order']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['order', 'name']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'level', 'status', 'xp_reward', 'is_featured']
    list_filter = ['category', 'level', 'status', 'is_featured']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ModuleInline]
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'description', 'short_description')
        }),
        ('Categorization', {
            'fields': ('category', 'level', 'thumbnail')
        }),
        ('Rewards & Duration', {
            'fields': ('xp_reward', 'estimated_duration')
        }),
        ('Status', {
            'fields': ('status', 'is_featured', 'created_by')
        }),
    )


@admin.register(CoursePrerequisite)
class CoursePrerequisiteAdmin(admin.ModelAdmin):
    list_display = ['course', 'prerequisite']
    list_filter = ['course']


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'requires_previous']
    list_filter = ['course', 'requires_previous']
    search_fields = ['title']
    inlines = [LessonInline]


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'content_type', 'order', 'xp_reward']
    list_filter = ['module__course', 'content_type', 'requires_lab_completion']
    search_fields = ['title', 'content']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(LessonResource)
class LessonResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'resource_type']
    list_filter = ['resource_type']


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'passing_score', 'max_attempts']
    inlines = [QuizQuestionInline]


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'quiz', 'question_type', 'points']
    list_filter = ['question_type']
    inlines = [QuizAnswerInline]


@admin.register(QuizAnswer)
class QuizAnswerAdmin(admin.ModelAdmin):
    list_display = ['answer_text', 'question', 'is_correct']
    list_filter = ['is_correct']


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score', 'passed', 'submitted_at', 'xp_awarded']
    list_filter = ['passed', 'xp_awarded', 'quiz__lesson__module__course']
    search_fields = ['user__email', 'quiz__title']
    readonly_fields = ['started_at', 'submitted_at']
    date_hierarchy = 'submitted_at'


@admin.register(AssessmentSession)
class AssessmentSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'session_type', 'quiz', 'started_at', 'is_active', 'submitted', 'ip_address']
    list_filter = ['session_type', 'is_active', 'submitted']
    search_fields = ['user__email', 'session_token', 'ip_address']
    readonly_fields = ['session_token', 'started_at', 'expires_at', 'submitted_at']
    date_hierarchy = 'started_at'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'session_type', 'quiz', 'session_token')
        }),
        ('Timing', {
            'fields': ('started_at', 'expires_at', 'submitted_at')
        }),
        ('Security', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Status', {
            'fields': ('is_active', 'submitted')
        }),
    )


@admin.register(AssessmentAuditLog)
class AssessmentAuditLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'user', 'event_type', 'severity', 'quiz', 'message_preview', 'ip_address']
    list_filter = ['event_type', 'severity', 'created_at']
    search_fields = ['user__email', 'message', 'ip_address']
    readonly_fields = ['created_at', 'user', 'event_type', 'severity', 'message', 'metadata', 'ip_address', 'user_agent']
    date_hierarchy = 'created_at'
    
    def message_preview(self, obj):
        return obj.message[:75] + '...' if len(obj.message) > 75 else obj.message
    message_preview.short_description = 'Message'
    
    fieldsets = (
        (None, {
            'fields': ('user', 'session', 'quiz')
        }),
        ('Event Details', {
            'fields': ('event_type', 'severity', 'message', 'metadata')
        }),
        ('Security', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
