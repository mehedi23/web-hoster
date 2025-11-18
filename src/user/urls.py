from django.urls import path
from user import views

urlpatterns = [
    # Authentication
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Email verification
    path('email-verification-sent/', views.email_verification_sent_view, name='email_verification_sent'),
    path('verify-email/<uuid:token>/', views.email_verify_view, name='email_verify'),
    path('resend-verification/', views.resend_verification_view, name='resend_verification'),

    # Password reset (for logged-in users)
    path('password-reset/', views.password_reset_view, name='password_reset'),

    # Forgot password (for non-logged-in users)
    path('forgot-password/', views.forgot_password_view, name='forgot_password'),
    path('password-reset-sent/', views.password_reset_sent_view, name='password_reset_sent'),
    path('reset-password/<uuid:token>/', views.password_reset_confirm_view, name='password_reset_confirm'),
]
