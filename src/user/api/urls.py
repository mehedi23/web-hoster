from django.urls import path
from user.api.views.auth import (
    register,
    email_verification,
    login,
    refresh_access_token,
)

app_name = 'user_api'

urlpatterns = [
    path('auth/register/', register, name='register'),
    path('auth/verify-email/', email_verification, name='verify_email'),
    path('auth/login/', login, name='login'),
    path('auth/refresh/', refresh_access_token, name='refresh_token'),
]
