from django.db import models
from django.utils import timezone
from datetime import timedelta
import uuid
from user.models.auth import User


class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_verification_tokens')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        """Check if token is still valid (not used and not expired)"""
        return not self.is_used

    def can_resend(self):
        """Check if 10 minutes have passed since last token creation"""
        return timezone.now() >= self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"Email verification token for {self.user.email}"

    class Meta:
        ordering = ['-created_at']


class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_tokens')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_valid(self):
        """Check if token is still valid (not used and not expired - 24 hours)"""
        expiry_time = self.created_at + timedelta(hours=24)
        return not self.is_used and timezone.now() < expiry_time

    def can_resend(self):
        """Check if 10 minutes have passed since last token creation"""
        return timezone.now() >= self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"Password reset token for {self.user.email}"

    class Meta:
        ordering = ['-created_at']
