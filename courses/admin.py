"""
Admin configuration for Course models.
"""
from django.contrib import admin
from .models import (
    Category, Course, CoursePrerequisite, Module, 
    Lesson, LessonResource, Quiz, QuizQuestion, QuizAnswer
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
