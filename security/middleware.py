"""
Security middleware for Terminal Academy.
PythonAnywhere-compatible (no Redis required).
"""
import logging
from django.utils import timezone

from .models import AuditLog, BlockedIP
from users.auth import get_client_ip

logger = logging.getLogger('security')


class AuditLogMiddleware:
    """
    Middleware to log requests for security auditing.
    """
    
    # Paths to exclude from logging (reduce noise)
    EXCLUDED_PATHS = [
        '/static/',
        '/media/',
        '/favicon.ico',
        '/__debug__/',
        '/health/',
    ]
    
    # Only log these actions (not every request)
    LOGGED_PATTERNS = [
        '/login',
        '/register',
        '/admin',
        '/api/v1/auth/',
        '/api/v1/labs/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Skip excluded paths
        if any(request.path.startswith(p) for p in self.EXCLUDED_PATHS):
            return self.get_response(request)
        
        # Get response
        response = self.get_response(request)
        
        # Only log specific actions
        if any(p in request.path for p in self.LOGGED_PATTERNS):
            try:
                self._log_request(request, response)
            except Exception as e:
                logger.error(f'Failed to log request: {e}')
        
        return response
    
    def _log_request(self, request, response):
        """Log request to audit log."""
        action = self._determine_action(request)
        
        if action:
            AuditLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                action=action,
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                request_path=request.path[:500],
                request_method=request.method,
                response_status=response.status_code,
            )
    
    def _determine_action(self, request) -> str:
        """Determine the action type based on the request."""
        path = request.path.lower()
        
        if '/login' in path and request.method == 'POST':
            return AuditLog.Action.LOGIN
        elif '/logout' in path:
            return AuditLog.Action.LOGOUT
        elif '/register' in path and request.method == 'POST':
            return AuditLog.Action.REGISTER
        elif '/labs/' in path and '/execute' in path:
            return AuditLog.Action.COMMAND_EXECUTE
        elif '/labs/' in path:
            return AuditLog.Action.LAB_ACCESS
        elif '/admin/' in path and request.method in ['POST', 'PUT', 'DELETE']:
            return AuditLog.Action.ADMIN_ACTION
        
        return None  # Don't log


class IPBlockMiddleware:
    """
    Middleware to block requests from blocked IPs.
    Uses database instead of Redis cache.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self._cache = {}
        self._cache_time = None
        self._cache_ttl = 60  # Refresh every 60 seconds
    
    def __call__(self, request):
        ip = get_client_ip(request)
        
        if self._is_blocked(ip):
            from django.http import HttpResponseForbidden
            logger.warning(f'Blocked IP attempted access: {ip}')
            return HttpResponseForbidden(
                'Access denied. Your IP has been blocked.'
            )
        
        return self.get_response(request)
    
    def _is_blocked(self, ip):
        """Check if IP is blocked using simple database cache."""
        self._refresh_cache()
        return ip in self._cache
    
    def _refresh_cache(self):
        """Refresh the blocked IPs from database."""
        now = timezone.now()
        
        if self._cache_time is None or (now - self._cache_time).seconds > self._cache_ttl:
            try:
                from django.db import models
                blocked = BlockedIP.objects.filter(
                    models.Q(blocked_until__isnull=True) | 
                    models.Q(blocked_until__gt=now)
                ).values_list('ip_address', flat=True)
                
                self._cache = set(blocked)
                self._cache_time = now
            except Exception as e:
                logger.error(f'Failed to refresh blocked IPs: {e}')
