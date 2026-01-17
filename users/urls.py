"""
URL patterns for user authentication API.
"""
from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # Authentication
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('token/refresh/', views.token_refresh, name='token_refresh'),
    
    # User profile
    path('me/', views.me, name='me'),
    path('me/update/', views.update_profile, name='update_profile'),
    
    # Ethical agreement & skill assessment
    path('ethical-agreement/', views.accept_ethical_agreement, name='ethical_agreement'),
    path('skill-assessment/', views.submit_skill_assessment, name='skill_assessment'),
]
