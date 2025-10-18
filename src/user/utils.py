from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from celery import shared_task


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return f"{user.pk}{timestamp}{user.is_active}"


email_verification_token = EmailVerificationTokenGenerator()


@shared_task
def send_verification_email(user_email, verification_link):
    subject = 'Verify your email'
    message = f'Click the link to verify your email: {verification_link}'
    from_email = 'noreply@example.com'
    recipient_list = [user_email]
    send_mail(subject, message, from_email, recipient_list)