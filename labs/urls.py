"""
URL patterns for labs API.
"""
from django.urls import path
from . import views

app_name = 'labs'

urlpatterns = [
    # Lab listing and details
    path('', views.lab_list, name='lab_list'),
    path('my-attempts/', views.my_lab_attempts, name='my_attempts'),
    path('<int:lab_id>/', views.lab_detail, name='lab_detail'),
    
    # Lab interaction
    path('<int:lab_id>/start/', views.start_lab, name='start_lab'),
    path('<int:lab_id>/execute/', views.execute_command, name='execute_command'),
    path('<int:lab_id>/hint/', views.get_hint, name='get_hint'),
    path('<int:lab_id>/submit/', views.submit_flag, name='submit_flag'),
    path('<int:lab_id>/submit-flag/', views.submit_flag, name='submit_flag_alt'),
    path('<int:lab_id>/reset/', views.reset_lab, name='reset_lab'),
    path('<int:lab_id>/solution-viewed/', views.solution_viewed, name='solution_viewed'),
]

