from rest_framework_simplejwt.views import TokenObtainPairView

class LoginView(TokenObtainPairView):
    """
    JWT-based login view for client-side API.
    Returns access and refresh tokens on successful authentication.
    """
    pass
