from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import authenticate, login
from rest_framework.generics import CreateAPIView
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from user.api.serializers import UserRegisterSerializer, UserLoginSerializer, PasswordResetSerializer
from user.utils import email_verification_token, send_verification_email


User = get_user_model()


class RegisterView(CreateAPIView):
    """
    API view for user registration using DRF's CreateAPIView.
    Allows anyone to register.
    """
    permission_classes = [AllowAny]
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            # Send verification email
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = email_verification_token.make_token(user)
            verification_link = request.build_absolute_uri(f'/verify-email/?uid={uid}&token={token}')
            send_verification_email.delay(user.email, verification_link)
            return Response(
                {'success_message': 'User registration successful. Verification email sent.'},
                status=status.HTTP_201_CREATED
            )
        except ValidationError as e:
            return Response(
                {
                    'success': False,
                    'message': 'Registration failed.',
                    'errors': e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class LoginView(generics.GenericAPIView):
    """
    API view for user login using DRF's GenericAPIView.
    Returns authentication token on successful login.
    """
    permission_classes = [AllowAny]
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            login(request, user)
            return Response(
                {
                    'success': True,
                    'message': 'Login successful.',
                },
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {
                    'success': False,
                    'message': 'Login failed.',
                    'errors': e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class PasswordResetView(generics.GenericAPIView):
    """
    API view for password reset using DRF's GenericAPIView.
    Requires authentication and current password verification.
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PasswordResetSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = request.user

            # Verify old password
            if not user.check_password(serializer.validated_data['old_password']):
                raise ValidationError({'old_password': ['Current password is incorrect.']})

            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()

            return Response(
                {
                    'success': True,
                    'message': 'Password updated successfully.',
                },
                status=status.HTTP_200_OK
            )
        except ValidationError as e:
            return Response(
                {
                    'success': False,
                    'message': 'Password update failed.',
                    'errors': e.detail
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class SendVerificationEmailView(generics.GenericAPIView):
    """
    API view for sending email verification.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response(
                {'success': False, 'message': 'Email is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                return Response(
                    {'success': False, 'message': 'Email already verified.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = email_verification_token.make_token(user)
            verification_link = request.build_absolute_uri(f'/verify-email/?uid={uid}&token={token}')
            send_verification_email.delay(user.email, verification_link)
            return Response(
                {'success': True, 'message': 'Verification email sent.'},
                status=status.HTTP_200_OK
            )
        except User.DoesNotExist:
            return Response(
                {'success': False, 'message': 'User not found.'},
                status=status.HTTP_404_NOT_FOUND
            )


class VerifyEmailView(generics.GenericAPIView):
    """
    API view for verifying email with token.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        if not uidb64 or not token:
            return Response(
                {'success': False, 'message': 'UID and token are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            from django.utils.http import urlsafe_base64_decode
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            if email_verification_token.check_token(user, token):
                user.is_active = True
                user.save()
                return Response(
                    {'success': True, 'message': 'Email verified successfully.'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'success': False, 'message': 'Invalid token.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {'success': False, 'message': 'Invalid link.'},
                status=status.HTTP_400_BAD_REQUEST
            )