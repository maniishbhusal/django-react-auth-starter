"""Djoser/SimpleJWT view subclasses with per-endpoint rate limiting."""

from djoser.views import UserViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .throttles import (
    LoginRateThrottle,
    PasswordResetRateThrottle,
    RegisterRateThrottle,
)


class ThrottledTokenObtainPairView(TokenObtainPairView):
    throttle_classes = [LoginRateThrottle]


class ThrottledTokenRefreshView(TokenRefreshView):
    throttle_classes = [LoginRateThrottle]


class ThrottledUserViewSet(UserViewSet):
    """Apply stricter throttles to registration and password-reset actions."""

    def get_throttles(self):
        if self.action == "create":
            return [RegisterRateThrottle()]
        if self.action in {
            "reset_password",
            "reset_password_confirm",
            "resend_activation",
        }:
            return [PasswordResetRateThrottle()]
        return super().get_throttles()
