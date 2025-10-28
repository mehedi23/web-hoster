from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from user.api.serializers import (
    ForgotPasswordSerializer,
    ForgotPasswordOTPVerificationSerializer,
    ResendOTPSerializer,
    SetNewPasswordSerializer
)
from user.api.services import AuthService
from user.models.auth import OTP
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    """
    Send OTP to user's email for password reset.

    Request body:
    {
        "email": "user@example.com"
    }

    Response:
    {
        "message": "OTP sent to your email."
    }
    """
    serializer = ForgotPasswordSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"message": "User with this email does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if user can request OTP (1-minute cooldown)
        can_request, message = AuthService.can_resend_otp(user)
        if not can_request:
            return Response(
                {"message": message},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Delete old OTPs and create new one
        OTP.objects.filter(user=user).delete()
        otp = AuthService.create_otp_for_user(user)

        # Send OTP to user's email
        from django.core.mail import send_mail
        try:
            send_mail(
                subject='Password Reset OTP',
                message=f'Your password reset OTP is: {otp.code}\n\nThis OTP will expire in 10 minutes.',
                from_email='noreply@web-hoster.com',
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending email: {str(e)}")

        return Response(
            {"message": "OTP sent to your email."},
            status=status.HTTP_200_OK
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_forgot_password_otp(request):
    """
    Verify OTP for forgot password flow.

    Request body:
    {
        "email": "user@example.com",
        "otp_code": "123456"
    }

    Response:
    {
        "message": "OTP verified successfully.",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    """
    serializer = ForgotPasswordOTPVerificationSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp_code']

        # Verify OTP
        user, is_valid, message = AuthService.verify_forgot_password_otp(email, otp_code)

        if is_valid and user:
            # Set is_mail_verified to true if it's false
            if not user.is_mail_verified:
                user.is_mail_verified = True
                user.save()

            # Delete the OTP record
            OTP.objects.filter(user=user, code=otp_code, is_used=True).delete()

            # Generate forgot password token with 1 hour expiration
            tokens = AuthService.generate_forgot_password_token(user)

            return Response(
                {
                    "message": "OTP verified successfully.",
                    "access": tokens['access']
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
def resend_otp(request):
    """
    Resend OTP for forgot password.

    Request body:
    {
        "email": "user@example.com"
    }

    Response:
    {
        "message": "OTP resent to your email."
    }
    """
    serializer = ResendOTPSerializer(data=request.data)

    if serializer.is_valid():
        email = serializer.validated_data['email']

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {"message": "User with this email does not exist."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check if user can resend OTP (1-minute cooldown)
        can_resend, message = AuthService.can_resend_otp(user)
        if not can_resend:
            return Response(
                {"message": message},
                status=status.HTTP_429_TOO_MANY_REQUESTS
            )

        # Delete old OTPs and create new one
        OTP.objects.filter(user=user).delete()
        otp = AuthService.create_otp_for_user(user)

        # Send OTP to user's email
        from django.core.mail import send_mail
        try:
            send_mail(
                subject='Password Reset OTP',
                message=f'Your password reset OTP is: {otp.code}\n\nThis OTP will expire in 10 minutes.',
                from_email='noreply@web-hoster.com',
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending email: {str(e)}")

        return Response(
            {"message": "OTP resent to your email."},
            status=status.HTTP_200_OK
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_new_password(request):
    """
    Set new password after forgot password OTP verification.
    Requires the access token obtained from verify_forgot_password_otp endpoint.
    The token must have 'new_password': true in its payload.

    Request body:
    {
        "new_password": "newpassword123",
        "confirm_password": "newpassword123"
    }

    Response:
    {
        "message": "Password has been reset successfully.",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    """
    # Get the token from the request
    jwt_authenticator = JWTAuthentication()

    try:
        # Validate token and get user
        validated_token = jwt_authenticator.get_validated_token(
            jwt_authenticator.get_raw_token(jwt_authenticator.get_header(request))
        )

        # Check if the token has 'new_password' claim set to true
        if not validated_token.get('new_password', False):
            return Response(
                {"message": "This endpoint requires a forgot password token."},
                status=status.HTTP_403_FORBIDDEN
            )

    except (InvalidToken, Exception) as e:
        return Response(
            {"message": "Invalid or expired token."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    user = request.user
    serializer = SetNewPasswordSerializer(data=request.data)

    if serializer.is_valid():
        new_password = serializer.validated_data['new_password']

        # Set new password
        user.set_password(new_password)
        user.save()

        # Generate new access and refresh tokens
        tokens = AuthService.generate_tokens(user)

        return Response(
            {
                "message": "Password has been reset successfully.",
                "access": tokens['access'],
                "refresh": tokens['refresh']
            },
            status=status.HTTP_200_OK
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST
    )
