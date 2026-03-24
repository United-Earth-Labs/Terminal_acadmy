"""
URL patterns for progress API.
"""
from django.urls import path
from . import views

app_name = 'progress'

urlpatterns = [
    path('stats/', views.my_stats, name='my_stats'),
    path('xp/', views.my_xp, name='my_xp'),
    path('xp/history/', views.my_xp_history, name='xp_history'),
    path('courses/', views.my_progress, name='my_progress'),
    path('achievements/', views.my_achievements, name='my_achievements'),
    path('achievements/all/', views.all_achievements, name='all_achievements'),
    path('leaderboard/', views.leaderboard, name='leaderboard'),
]
