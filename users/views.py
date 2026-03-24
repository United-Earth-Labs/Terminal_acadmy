"""
API views for user authentication and management.
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth import get_user_model

from .auth import generate_token_pair, refresh_access_token, verify_otp, get_client_ip
from .serializers import (
    UserSerializer, 
    LoginSerializer, 
    RegisterSerializer,
    TokenRefreshSerializer
)
from .permissions import HasAcceptedEthicalAgreement

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """Register a new user."""
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        access_token, refresh_token = generate_token_pair(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': access_token,
                'refresh': refresh_token,
            },
            'message': 'Registration successful. Please accept the ethical agreement.',
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """Login a user and return JWT tokens."""
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        otp_code = serializer.validated_data.get('otp_code')
        
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {'error': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if account is locked
        if user.is_account_locked:
            return Response(
                {'error': 'Account is locked. Please try again later.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Verify password
        if not user.check_password(password):
            user.record_failed_login()
            return Response(
                {'error': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verify OTP if enabled
        if user.otp_enabled:
            if not otp_code:
                return Response(
                    {'error': 'OTP code required.', 'otp_required': True},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            if not verify_otp(user.otp_secret, otp_code):
                return Response(
                    {'error': 'Invalid OTP code.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        
        # Record successful login
        ip_address = get_client_ip(request)
        user.record_successful_login(ip_address)
        
        # Generate tokens
        access_token, refresh_token = generate_token_pair(user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': access_token,
                'refresh': refresh_token,
            },
            'ethical_agreement_required': not user.ethical_agreement_accepted,
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def token_refresh(request):
    """Refresh an access token using a refresh token."""
    serializer = TokenRefreshSerializer(data=request.data)
    
    if serializer.is_valid():
        refresh_token = serializer.validated_data['refresh']
        new_access_token = refresh_access_token(refresh_token)
        
        if new_access_token:
            return Response({
                'access': new_access_token,
            })
        
        return Response(
            {'error': 'Invalid or expired refresh token.'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    """Get current user's profile."""
    return Response(UserSerializer(request.user).data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request):
    """Update current user's profile."""
    serializer = UserSerializer(request.user, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def accept_ethical_agreement(request):
    """Accept the ethical hacking agreement."""
    user = request.user
    
    if user.ethical_agreement_accepted:
        return Response({'message': 'Agreement already accepted.'})
    
    ip_address = get_client_ip(request)
    user.accept_ethical_agreement(ip_address)
    
    return Response({
        'message': 'Ethical agreement accepted.',
        'accepted_at': user.ethical_agreement_accepted_at,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_skill_assessment(request):
    """Submit skill assessment answers with rate limiting and audit logging."""
    from .services import (
        process_skill_assessment,
        check_skill_assessment_rate_limit
    )
    from django.utils import timezone
    
    # Check rate limiting
    rate_check = check_skill_assessment_rate_limit(request.user, request)
    if not rate_check['allowed']:
        return Response(
            {
                'error': rate_check['error'],
                'cooldown_remaining_hours': rate_check.get('cooldown_remaining_hours')
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS
        )
    
    # Get answers from request
    answers = request.data.get('answers', {})
    
    # Process with enhanced validation and logging
    result = process_skill_assessment(answers, user=request.user, request=request)
    
    if not result['success']:
        return Response(
            {'error': result['error']},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update user skill level
    request.user.skill_level = result['skill_level']
    request.user.skill_assessment_completed_at = timezone.now()
    request.user.save(update_fields=['skill_level', 'skill_assessment_completed_at'])
    
    return Response({
        'skill_level': result['skill_level'],
        'score': result['score'],
        'total': result['total'],
        'message': f'Your skill level has been set to {result["skill_level"]}.',
    })

