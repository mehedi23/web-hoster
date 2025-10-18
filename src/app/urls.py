from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from user.views import home, sign_in, register, email_verification, logout_view

urlpatterns = [
    path('', home, name='home'),
    path('sign-in/', sign_in, name='sign_in'),
    path('register/', register, name='register'),
    path('verify-email/', email_verification, name='verify_email'),
    path('logout/', logout_view, name='logout'),
    
    path('admin/', admin.site.urls),
    path('api/user/', include('user.api.urls')),
]
