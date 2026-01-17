"""
URL patterns for web views (template-based pages).
"""
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('ethical-agreement/', views.ethical_agreement, name='ethical_agreement'),
    path('skill-assessment/', views.skill_assessment, name='skill_assessment'),
    
    # Additional pages
    path('courses/', views.courses_view, name='courses'),
    path('courses/<slug:slug>/', views.course_detail_view, name='course_detail'),
    path('labs/', views.labs_view, name='labs'),
    path('labs/<int:lab_id>/', views.lab_detail_view, name='lab_detail'),
    path('achievements/', views.achievements_view, name='achievements'),
    path('profile/', views.profile_view, name='profile'),
    path('leaderboard/', views.leaderboard_view, name='leaderboard'),
]


