from django.urls import path
from .views.server_site import RegisterView, LoginView, PasswordResetView, SendVerificationEmailView, VerifyEmailView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('password-reset/', PasswordResetView.as_view(), name='password-reset'),
    path('send-verification-email/', SendVerificationEmailView.as_view(), name='send-verification-email'),
    path('verify-email/', VerifyEmailView.as_view(), name='verify-email'),
]