from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta

from user.forms import (
    SignUpForm, LoginForm, PasswordResetForm,
    ForgotPasswordEmailForm, SetNewPasswordForm
)
from user.models.tokens import EmailVerificationToken, PasswordResetToken
from user.utils import send_verification_email, send_password_reset_email

User = get_user_model()


def signup_view(request):
    """User signup with email verification"""
    if request.user.is_authenticated:
        return redirect('admin:index')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Send verification email
            send_verification_email(user, request)
            messages.success(
                request,
                'Account created successfully! Please check your email to verify your account.'
            )
            return redirect('email_verification_sent')
    else:
        form = SignUpForm()

    return render(request, 'user/signup.html', {'form': form})


def email_verification_sent_view(request):
    """Display message that verification email has been sent"""
    return render(request, 'user/email_verification_sent.html')


def email_verify_view(request, token):
    """Verify email using token from email link"""
    verification_token = get_object_or_404(EmailVerificationToken, token=token)

    if not verification_token.is_valid():
        messages.error(request, 'This verification link has already been used.')
        return redirect('login')

    # Mark token as used and verify user's email
    verification_token.is_used = True
    verification_token.save()

    user = verification_token.user
    user.is_mail_verified = True
    user.save()

    messages.success(request, 'Email verified successfully! You can now log in.')
    return redirect('login')


def resend_verification_view(request):
    """Resend email verification link"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)

            if user.is_mail_verified:
                messages.info(request, 'This email is already verified.')
                return redirect('login')

            # Check if user can resend (10 minutes passed since last token)
            latest_token = EmailVerificationToken.objects.filter(user=user).first()

            if latest_token and not latest_token.can_resend():
                time_remaining = (latest_token.created_at + timedelta(minutes=10)) - timezone.now()
                minutes = int(time_remaining.total_seconds() / 60)
                messages.warning(
                    request,
                    f'Please wait {minutes + 1} more minute(s) before requesting another verification email.'
                )
                return redirect('resend_verification')

            # Send new verification email
            send_verification_email(user, request)
            messages.success(request, 'Verification email sent! Please check your inbox.')
            return redirect('email_verification_sent')

        except User.DoesNotExist:
            messages.error(request, 'No account found with this email address.')

    return render(request, 'user/resend_verification.html')


def login_view(request):
    """User login with email verification check"""
    if request.user.is_authenticated:
        return redirect('admin:index')

    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)

            if user is not None:
                # Check if email is verified
                if not user.is_mail_verified:
                    messages.warning(
                        request,
                        'Please verify your email before logging in. Check your inbox for the verification link.'
                    )
                    return redirect('resend_verification')

                login(request, user)
                messages.success(request, f'Welcome back, {user.email}!')
                return redirect('admin:index')
    else:
        form = LoginForm()

    return render(request, 'user/login.html', {'form': form})


@login_required
def logout_view(request):
    """User logout"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


@login_required
def password_reset_view(request):
    """Password reset for logged-in users (requires old password)"""
    if request.method == 'POST':
        form = PasswordResetForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password changed successfully!')
            return redirect('admin:index')
    else:
        form = PasswordResetForm(request.user)

    return render(request, 'user/password_reset.html', {'form': form})


def forgot_password_view(request):
    """Forgot password - send reset email"""
    if request.user.is_authenticated:
        return redirect('admin:index')

    if request.method == 'POST':
        form = ForgotPasswordEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = User.objects.get(email=email)

            # Check if user can resend (10 minutes passed since last token)
            latest_token = PasswordResetToken.objects.filter(user=user).first()

            if latest_token and not latest_token.can_resend():
                time_remaining = (latest_token.created_at + timedelta(minutes=10)) - timezone.now()
                minutes = int(time_remaining.total_seconds() / 60)
                messages.warning(
                    request,
                    f'Please wait {minutes + 1} more minute(s) before requesting another reset email.'
                )
                return redirect('forgot_password')

            # Send password reset email
            send_password_reset_email(user, request)
            messages.success(request, 'Password reset email sent! Please check your inbox.')
            return redirect('password_reset_sent')
    else:
        form = ForgotPasswordEmailForm()

    return render(request, 'user/forgot_password.html', {'form': form})


def password_reset_sent_view(request):
    """Display message that password reset email has been sent"""
    return render(request, 'user/password_reset_sent.html')


def password_reset_confirm_view(request, token):
    """Confirm password reset and set new password"""
    reset_token = get_object_or_404(PasswordResetToken, token=token)

    if not reset_token.is_valid():
        messages.error(request, 'This password reset link has expired or already been used.')
        return redirect('forgot_password')

    if request.method == 'POST':
        form = SetNewPasswordForm(request.POST)
        if form.is_valid():
            user = reset_token.user

            # Set new password
            user.set_password(form.cleaned_data['new_password'])

            # If email was not verified, verify it now
            if not user.is_mail_verified:
                user.is_mail_verified = True

            user.save()

            # Mark token as used
            reset_token.is_used = True
            reset_token.save()

            messages.success(request, 'Password reset successfully! You can now log in with your new password.')
            return redirect('login')
    else:
        form = SetNewPasswordForm()

    return render(request, 'user/password_reset_confirm.html', {'form': form, 'token': token})
