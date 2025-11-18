from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from user.models.tokens import EmailVerificationToken, PasswordResetToken


def send_verification_email(user, request):
    """
    Create a new email verification token and send verification email to user
    """
    # Create new verification token
    token = EmailVerificationToken.objects.create(user=user)

    # Build verification URL
    verification_url = request.build_absolute_uri(
        reverse('email_verify', kwargs={'token': str(token.token)})
    )

    # Email content
    subject = 'Verify Your Email Address'
    message = f"""
    Hello,

    Thank you for signing up! Please verify your email address by clicking the link below:

    {verification_url}

    This link will remain valid until you use it.

    If you did not create an account, please ignore this email.

    Best regards,
    The Team
    """

    # Send email
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
        [user.email],
        fail_silently=False,
    )

    return token


def send_password_reset_email(user, request):
    """
    Create a new password reset token and send reset email to user
    """
    # Create new password reset token
    token = PasswordResetToken.objects.create(user=user)

    # Build reset URL
    reset_url = request.build_absolute_uri(
        reverse('password_reset_confirm', kwargs={'token': str(token.token)})
    )

    # Email content
    subject = 'Reset Your Password'
    message = f"""
    Hello,

    You requested to reset your password. Please click the link below to set a new password:

    {reset_url}

    This link will expire in 24 hours.

    If you did not request a password reset, please ignore this email.

    Best regards,
    The Team
    """

    # Send email
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@example.com',
        [user.email],
        fail_silently=False,
    )

    return token
