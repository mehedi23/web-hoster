from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError


class EmailVerificationMiddleware(MiddlewareMixin):
    """
    Middleware to restrict unverified users to only access auth endpoints.

    Rules:
    - If user is authenticated and is_mail_verified is False and not a superuser,
      they can only access URLs that start with '/api/user/auth/'
    - Superusers and verified users have full access
    - Unauthenticated users have full access
    """

    ALLOWED_URL_PREFIX = '/api/user/auth/'

    def process_request(self, request):
        """Process the request and check email verification status"""

        # Skip middleware for allowed auth endpoints
        if request.path.startswith(self.ALLOWED_URL_PREFIX):
            return None

        # Try to get the authenticated user from JWT token
        user = self.get_user_from_token(request)

        # If no authenticated user, allow access
        if not user:
            return None

        # If user is superuser, allow access
        if user.is_superuser:
            return None

        # If user is authenticated but email is not verified, deny access
        if not user.is_mail_verified:
            return JsonResponse(
                {
                    'message': 'Email verification required. Please verify your email before accessing this resource.',
                    'error': 'email_not_verified'
                },
                status=403
            )

        # User is verified, allow access
        return None

    def get_user_from_token(self, request):
        """Extract and validate JWT token to get the user"""
        try:
            jwt_authenticator = JWTAuthentication()

            # Get the authorization header
            header = jwt_authenticator.get_header(request)
            if header is None:
                return None

            # Get the raw token
            raw_token = jwt_authenticator.get_raw_token(header)
            if raw_token is None:
                return None

            # Validate the token
            validated_token = jwt_authenticator.get_validated_token(raw_token)

            # Get the user from the token
            user = jwt_authenticator.get_user(validated_token)

            return user

        except (InvalidToken, TokenError, Exception):
            # If token is invalid or any error occurs, return None
            return None
