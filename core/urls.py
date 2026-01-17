"""
URL configuration for Terminal Academy project.

The `urlpatterns` list routes URLs to views.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Health check (for Docker/load balancer)
    path('health/', lambda request: __import__('django.http', fromlist=['JsonResponse']).JsonResponse({'status': 'ok'})),
    
    # API endpoints
    path('api/v1/auth/', include('users.urls', namespace='users')),
    path('api/v1/courses/', include('courses.urls', namespace='courses')),
    path('api/v1/labs/', include('labs.urls', namespace='labs')),
    path('api/v1/progress/', include('progress.urls', namespace='progress')),
    
    # Web views
    path('', include('core.views_urls')),
]

# Debug toolbar (development only)
if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
    
    # Serve media files in development
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom admin header
admin.site.site_header = 'Terminal Academy Administration'
admin.site.site_title = 'Terminal Academy Admin'
admin.site.index_title = 'Welcome to Terminal Academy Administration'
