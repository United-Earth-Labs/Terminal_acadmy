"""
Serializers for Course API.
"""
from rest_framework import serializers
from .models import (
    Category, Course, Module, Lesson, 
    LessonResource, Quiz, QuizQuestion, QuizAnswer
)


class CategorySerializer(serializers.ModelSerializer):
    course_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'icon', 'course_count']
    
    def get_course_count(self, obj):
        return obj.courses.filter(status='published').count()


class LessonResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonResource
        fields = ['id', 'title', 'resource_type', 'url', 'file', 'description']


class QuizAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuizAnswer
        fields = ['id', 'answer_text', 'order']
        # Note: is_correct is NOT exposed to prevent cheating


class QuizQuestionSerializer(serializers.ModelSerializer):
    answers = QuizAnswerSerializer(many=True, read_only=True)
    
    class Meta:
        model = QuizQuestion
        fields = ['id', 'question_text', 'question_type', 'order', 'points', 'answers']


class QuizSerializer(serializers.ModelSerializer):
    questions = QuizQuestionSerializer(many=True, read_only=True)
    question_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Quiz
        fields = ['id', 'title', 'passing_score', 'max_attempts', 'time_limit', 
                  'question_count', 'questions']
    
    def get_question_count(self, obj):
        return obj.questions.count()


class LessonListSerializer(serializers.ModelSerializer):
    """Minimal lesson info for listings."""
    has_lab = serializers.SerializerMethodField()
    has_quiz = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'slug', 'content_type', 'order', 
                  'xp_reward', 'estimated_duration', 'has_lab', 'has_quiz']
    
    def get_has_lab(self, obj):
        return obj.labs.exists()
    
    def get_has_quiz(self, obj):
        return hasattr(obj, 'quiz')


class LessonDetailSerializer(serializers.ModelSerializer):
    """Full lesson details."""
    resources = LessonResourceSerializer(many=True, read_only=True)
    quiz = QuizSerializer(read_only=True)
    has_lab = serializers.SerializerMethodField()
    
    class Meta:
        model = Lesson
        fields = ['id', 'title', 'slug', 'content_type', 'content', 
                  'video_url', 'order', 'requires_lab_completion',
                  'xp_reward', 'estimated_duration', 'resources', 
                  'quiz', 'has_lab']
    
    def get_has_lab(self, obj):
        return obj.labs.exists()


class ModuleListSerializer(serializers.ModelSerializer):
    """Module with lesson count."""
    lesson_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'order', 'lesson_count']


class ModuleDetailSerializer(serializers.ModelSerializer):
    """Module with full lessons."""
    lessons = LessonListSerializer(many=True, read_only=True)
    
    class Meta:
        model = Module
        fields = ['id', 'title', 'description', 'order', 'requires_previous', 'lessons']


class CourseListSerializer(serializers.ModelSerializer):
    """Minimal course info for listings."""
    category = CategorySerializer(read_only=True)
    module_count = serializers.ReadOnlyField()
    lesson_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'short_description', 'category', 
                  'level', 'thumbnail', 'xp_reward', 'estimated_duration',
                  'is_featured', 'module_count', 'lesson_count']


class CourseDetailSerializer(serializers.ModelSerializer):
    """Full course details with modules."""
    category = CategorySerializer(read_only=True)
    modules = ModuleDetailSerializer(many=True, read_only=True)
    prerequisites = serializers.SerializerMethodField()
    module_count = serializers.ReadOnlyField()
    lesson_count = serializers.ReadOnlyField()
    lab_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Course
        fields = ['id', 'title', 'slug', 'description', 'short_description',
                  'category', 'level', 'thumbnail', 'xp_reward', 
                  'estimated_duration', 'is_featured', 'module_count',
                  'lesson_count', 'lab_count', 'prerequisites', 'modules']
    
    def get_prerequisites(self, obj):
        prereqs = obj.prerequisites.select_related('prerequisite').all()
        return [
            {
                'id': p.prerequisite.id,
                'title': p.prerequisite.title,
                'slug': p.prerequisite.slug,
            }
            for p in prereqs
        ]
