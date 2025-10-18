from django.shortcuts import render, redirect
from django.contrib.auth import logout

# Create your views here.

def home(request):
    return render(request, 'home.html')

def sign_in(request):
    return render(request, 'sign_in.html')

def register(request):
    return render(request, 'register.html')

def email_verification(request):
    return render(request, 'email_verification.html')

def logout_view(request):
    logout(request)
    return redirect('/')
