from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from user.api.serializers import (
    RegisterSerializer,
    EmailVerificationSerializer,
    LoginSerializer,
    RefreshAccessTokenSerializer,
    UserDataSerializer
)
from user.api.services import AuthService

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Register a new user.
    
    The user will register using their email, password, and confirm password.
    After registration, a verification OTP will be sent to the user's email,
    which will be stored in the OTP model. The OTP will be valid for 10 minutes.
    
    Request body:
    {
        "email": "user@example.com",
        "password": "securepassword123",
        "confirm_password": "securepassword123"
    }
    
    Response:
    {
        "message": "Registration successful. OTP sent to your email.",
        "user": {
            "id": 1,
            "email": "user@example.com",
            "is_mail_verified": false,
            "date_joined": "2025-10-18T12:00:00Z"
        }
    }
    """
    serializer = RegisterSerializer(data=request.data)
    
    if serializer.is_valid():
        user = serializer.save()
        
        # Create OTP for the user
        otp = AuthService.create_otp_for_user(user)
        
        # Print OTP to console for development
        print(f"\n{'='*50}")
        print(f"OTP for {user.email}: {otp.code}")
        print(f"{'='*50}\n")
        
        # Send OTP to user's email using Django mail backend
        from django.core.mail import send_mail
        try:
            send_mail(
                subject='Email Verification OTP',
                message=f'Your email verification OTP is: {otp.code}\n\nThis OTP will expire in 10 minutes.',
                from_email='noreply@web-hoster.com',
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending email: {str(e)}")
        
        # Generate access token for unverified user
        tokens = AuthService.generate_access_token_only(user)
        
        return Response(
            {
                "message": "Registration successful. OTP sent to your email.",
                "email": user.email,
                "access_token": tokens['access']
            },
            status=status.HTTP_201_CREATED
        )
    
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def email_verification(request):
    """
    Verify user email using OTP.
    
    The user will send a request to this API using a JWT token.
    Only unverified users can verify their email.
    The verification link sent to the user's email will contain a token.
    The user will verify their email using that token.
    If the token is valid and within the allowed time, the user's email will be verified.
    If the token is invalid or expired, an error message will be returned.
    The user cannot attempt another email verification within 10 minutes.
    After successful verification, the token will be deleted from the OTP model.
    Once verified, the user will receive both an access token and a refresh token.
    The access token will be valid for 1 day, and the refresh token will be valid for 7 days.
    
    Request body:
    {
        "otp_code": "123456"
    }
    
    Response on success:
    {
        "message": "Email verified successfully.",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    """
    user = request.user
    
    # Check if user is already verified
    if user.is_mail_verified:
        return Response(
            {"message": "Your email is already verified."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Check if user can request OTP
    can_request, message = AuthService.can_request_new_otp(user)
    
    serializer = EmailVerificationSerializer(data=request.data)
    
    if serializer.is_valid():
        otp_code = serializer.validated_data['otp_code']
        
        # Verify OTP
        is_valid, message = AuthService.verify_otp(user, otp_code)
        
        if is_valid:
            # Mark user email as verified
            user.is_mail_verified = True
            user.save()
            
            # Delete the OTP from database
            from user.models.auth import OTP
            OTP.objects.filter(user=user, code=otp_code, is_used=True).delete()
            
            # Generate tokens for verified user
            tokens = AuthService.generate_tokens(user)
            
            return Response(
                {
                    "message": "Email verified successfully.",
                    "access": tokens['access'],
                    "refresh": tokens['refresh'],
                    "user": UserDataSerializer(user).data
                },
                status=status.HTTP_200_OK
            )
        
        return Response(
            {"message": message},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Login user with email and password.
    
    The user will log in using their email and password.
    If the email is not verified, only an access token will be generated.
    If the email is verified, both an access token and a refresh token will be generated.
    
    Request body:
    {
        "email": "user@example.com",
        "password": "securepassword123"
    }
    
    Response (verified user):
    {
        "message": "Login successful.",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "user": {...}
    }
    
    Response (unverified user):
    {
        "message": "Login successful. Please verify your email.",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "user": {...}
    }
    """
    serializer = LoginSerializer(data=request.data)
    
    if serializer.is_valid():
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Authenticate user
        user, error_message = AuthService.authenticate_user(email, password)
        
        if user:
            if user.is_mail_verified:
                # Generate both access and refresh tokens for verified users
                tokens = AuthService.generate_tokens(user)
                
                return Response(
                    {
                        "message": "Login successful.",
                        "access": tokens['access'],
                        "refresh": tokens['refresh'],
                        "user": UserDataSerializer(user).data
                    },
                    status=status.HTTP_200_OK
                )
            else:
                # Generate only access token for unverified users
                tokens = AuthService.generate_access_token_only(user)
                
                return Response(
                    {
                        "message": "Login successful. Please verify your email.",
                        "access": tokens['access'],
                        "user": UserDataSerializer(user).data
                    },
                    status=status.HTTP_200_OK
                )
        
        return Response(
            {"message": error_message},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_access_token(request):
    """
    Refresh the access token using the refresh token.
    
    The user will refresh the access token using the refresh token.
    
    Request body:
    {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    
    Response:
    {
        "message": "Access token refreshed successfully.",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    """
    serializer = RefreshAccessTokenSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            refresh_token = RefreshToken(serializer.validated_data['refresh'])
            access_token = refresh_token.access_token
            
            # Get user from token
            user_id = refresh_token.get('user_id')
            try:
                user = User.objects.get(id=user_id)
                access_token['is_mail_verified'] = user.is_mail_verified
                access_token['email'] = user.email
            except User.DoesNotExist:
                pass
            
            return Response(
                {
                    "message": "Access token refreshed successfully.",
                    "access": str(access_token)
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"message": "Invalid refresh token."},
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )
