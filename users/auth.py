"""
Authentication utilities for Terminal Academy.

This module provides JWT authentication, OTP generation/verification,
and password validation utilities.
"""
import jwt
import pyotp
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Tuple

from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    """
    JWT Authentication for Django REST Framework.
    """
    keyword = 'Bearer'
    
    def authenticate(self, request):
        """Authenticate the request using JWT token."""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header.startswith(self.keyword):
            return None
        
        try:
            token = auth_header.split()[1]
            payload = decode_jwt_token(token)
            user = User.objects.get(id=payload['user_id'])
            
            if not user.is_active:
                raise AuthenticationFailed('User account is disabled.')
            
            return (user, token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token.')
        except User.DoesNotExist:
            raise AuthenticationFailed('User not found.')
    
    def authenticate_header(self, request):
        """Return the 'WWW-Authenticate' header value."""
        return self.keyword


def generate_jwt_token(user, token_type='access') -> str:
    """
    Generate a JWT token for the given user.
    
    Args:
        user: The user object
        token_type: Either 'access' or 'refresh'
    
    Returns:
        The encoded JWT token string
    """
    if token_type == 'access':
        exp_delta = timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    else:
        exp_delta = timedelta(days=settings.JWT_REFRESH_EXPIRATION_DAYS)
    
    payload = {
        'user_id': user.id,
        'email': user.email,
        'role': user.role,
        'type': token_type,
        'iat': datetime.utcnow(),
        'exp': datetime.utcnow() + exp_delta,
    }
    
    return jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def decode_jwt_token(token: str) -> dict:
    """
    Decode and validate a JWT token.
    
    Args:
        token: The JWT token string
    
    Returns:
        The decoded payload dictionary
    
    Raises:
        jwt.ExpiredSignatureError: If token has expired
        jwt.InvalidTokenError: If token is invalid
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[settings.JWT_ALGORITHM]
    )


def generate_token_pair(user) -> Tuple[str, str]:
    """
    Generate both access and refresh tokens for a user.
    
    Returns:
        Tuple of (access_token, refresh_token)
    """
    access_token = generate_jwt_token(user, 'access')
    refresh_token = generate_jwt_token(user, 'refresh')
    return access_token, refresh_token


def refresh_access_token(refresh_token: str) -> Optional[str]:
    """
    Generate a new access token from a refresh token.
    
    Args:
        refresh_token: The refresh token string
    
    Returns:
        New access token or None if refresh token is invalid
    """
    try:
        payload = decode_jwt_token(refresh_token)
        
        if payload.get('type') != 'refresh':
            return None
        
        user = User.objects.get(id=payload['user_id'])
        
        if not user.is_active:
            return None
        
        return generate_jwt_token(user, 'access')
    except (jwt.InvalidTokenError, User.DoesNotExist):
        return None


# OTP Functions

def generate_otp_secret() -> str:
    """Generate a new OTP secret for a user."""
    return pyotp.random_base32()


def get_totp(secret: str) -> pyotp.TOTP:
    """Get a TOTP object for the given secret."""
    return pyotp.TOTP(secret)


def generate_otp(secret: str) -> str:
    """
    Generate a current OTP code for the given secret.
    
    Args:
        secret: The user's OTP secret
    
    Returns:
        The current OTP code
    """
    totp = get_totp(secret)
    return totp.now()


def verify_otp(secret: str, code: str) -> bool:
    """
    Verify an OTP code against the secret.
    
    Args:
        secret: The user's OTP secret
        code: The OTP code to verify
    
    Returns:
        True if the code is valid, False otherwise
    """
    if not secret or not code:
        return False
    
    totp = get_totp(secret)
    # Allow 1 step tolerance for clock skew
    return totp.verify(code, valid_window=1)


def get_otp_provisioning_uri(secret: str, email: str) -> str:
    """
    Get the provisioning URI for setting up OTP in an authenticator app.
    
    Args:
        secret: The user's OTP secret
        email: The user's email address
    
    Returns:
        The provisioning URI for QR code generation
    """
    totp = get_totp(secret)
    return totp.provisioning_uri(
        name=email,
        issuer_name='Terminal Academy'
    )


# Password Utilities

def hash_password(password: str) -> bytes:
    """
    Hash a password using bcrypt.
    
    Args:
        password: The plain text password
    
    Returns:
        The hashed password
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt)


def verify_password(password: str, hashed: bytes) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: The plain text password
        hashed: The hashed password
    
    Returns:
        True if the password matches, False otherwise
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed)


def get_client_ip(request) -> str:
    """
    Get the client's IP address from the request.
    
    Args:
        request: The HTTP request object
    
    Returns:
        The client's IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
