import random
import string
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from user.models.auth import OTP

User = get_user_model()


class AuthService:
    """Service class for authentication operations"""

    OTP_VALIDITY_MINUTES = 10
    ACCESS_TOKEN_LIFETIME_HOURS = 24
    REFRESH_TOKEN_LIFETIME_DAYS = 7

    @staticmethod
    def generate_otp(length=6):
        """Generate a random OTP code"""
        return ''.join(random.choices(string.digits, k=length))

    @staticmethod
    def create_otp_for_user(user):
        """Create and save OTP for a user"""
        # Delete any existing OTPs for this user
        OTP.objects.filter(user=user, is_used=False).delete()
        
        otp_code = AuthService.generate_otp()
        otp = OTP.objects.create(user=user, code=otp_code)
        return otp

    @staticmethod
    def verify_otp(user, otp_code):
        """Verify OTP for a user"""
        try:
            otp = OTP.objects.get(
                user=user,
                code=otp_code,
                is_used=False
            )
            
            # Check if OTP is expired (older than 10 minutes)
            if timezone.now() - otp.created_at > timedelta(minutes=AuthService.OTP_VALIDITY_MINUTES):
                return False, "OTP has expired."
            
            otp.is_used = True
            otp.save()
            return True, "OTP verified successfully."
        
        except OTP.DoesNotExist:
            return False, "Invalid OTP code."

    @staticmethod
    def can_request_new_otp(user):
        """Check if user can request a new OTP (not within 10 minutes of last request)"""
        recent_otp = OTP.objects.filter(user=user, is_used=False).order_by('-created_at').first()
        
        if not recent_otp:
            return True, "You can request OTP."
        
        time_diff = timezone.now() - recent_otp.created_at
        if time_diff < timedelta(minutes=AuthService.OTP_VALIDITY_MINUTES):
            remaining_time = AuthService.OTP_VALIDITY_MINUTES - int(time_diff.total_seconds() / 60)
            return False, f"Please wait {remaining_time} minutes before requesting a new OTP."
        
        return True, "You can request OTP."

    @staticmethod
    def generate_tokens(user):
        """Generate JWT tokens for a user"""
        refresh = RefreshToken.for_user(user)
        
        # Add custom claims to access token
        access = refresh.access_token
        access['is_mail_verified'] = user.is_mail_verified
        access['email'] = user.email
        
        return {
            'access': str(access),
            'refresh': str(refresh),
        }

    @staticmethod
    def generate_access_token_only(user):
        """Generate only access token for unverified users"""
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        access['is_mail_verified'] = user.is_mail_verified
        access['email'] = user.email
        
        return {
            'access': str(access),
        }

    @staticmethod
    def authenticate_user(email, password):
        """Authenticate user with email and password"""
        try:
            user = User.objects.get(email=email)
            if user.check_password(password) and user.is_active:
                return user, None
            return None, "Invalid email or password."
        except User.DoesNotExist:
            return None, "Invalid email or password."
