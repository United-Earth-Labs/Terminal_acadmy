"""
URL patterns for courses API.
"""
from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    # Categories
    path('categories/', views.category_list, name='category_list'),
    
    # Courses
    path('', views.course_list, name='course_list'),
    path('recommended/', views.recommended_courses, name='recommended'),
    path('<slug:slug>/', views.course_detail, name='course_detail'),
    
    # Modules
    path('<slug:course_slug>/modules/<int:module_id>/', 
         views.module_detail, name='module_detail'),
    
    # Lessons
    path('<slug:course_slug>/lessons/<slug:lesson_slug>/',
         views.lesson_detail, name='lesson_detail'),
    path('<slug:course_slug>/lessons/<slug:lesson_slug>/complete/',
         views.complete_lesson, name='complete_lesson'),
    
    # Quizzes
    path('quiz/<int:quiz_id>/start/', views.start_quiz, name='start_quiz'),
    path('quiz/<int:quiz_id>/submit/', views.submit_quiz, name='submit_quiz'),
]

