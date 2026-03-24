"""
Permission classes for role-based access control.
"""
from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    """Permission class for student access."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in ['student', 'mentor', 'admin']
        )


class IsMentor(BasePermission):
    """Permission class for mentor access."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role in ['mentor', 'admin']
        )


class IsAdmin(BasePermission):
    """Permission class for admin access."""
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.role == 'admin'
        )


class HasAcceptedEthicalAgreement(BasePermission):
    """
    Permission that requires the user to have accepted the ethical agreement.
    This is CRITICAL for accessing any lab content.
    """
    message = 'You must accept the ethical hacking agreement before accessing labs.'
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.ethical_agreement_accepted
        )


class IsAccountNotLocked(BasePermission):
    """Permission that checks if the account is not locked."""
    message = 'Your account is currently locked. Please try again later.'
    
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            not request.user.is_account_locked
        )


class IsOwnerOrAdmin(BasePermission):
    """Permission that allows access to owner or admin."""
    
    def has_object_permission(self, request, view, obj):
        # Admin has access to everything
        if request.user.role == 'admin':
            return True
        
        # Check if user owns the object
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        return obj == request.user
