from django.urls import path
from user.api.views.auth import (
    register,
    email_verification,
    login,
    refresh_access_token,
    reset_password,
)
from user.api.views.forgot_password import (
    forgot_password,
    verify_forgot_password_otp,
    resend_otp,
    set_new_password,
)

app_name = 'user_api'

urlpatterns = [
    path('auth/register/', register, name='register'),
    path('auth/verify-email/', email_verification, name='verify_email'),
    path('auth/login/', login, name='login'),
    path('auth/refresh/', refresh_access_token, name='refresh_token'),
    path('auth/reset-password/', reset_password, name='reset_password'),
    path('auth/forgot-password/', forgot_password, name='forgot_password'),
    path('auth/forgot-password/verify-otp/', verify_forgot_password_otp, name='verify_forgot_password_otp'),
    path('auth/forgot-password/resend-otp/', resend_otp, name='resend_otp'),
    path('auth/forgot-password/set-new-password/', set_new_password, name='set_new_password'),
]
