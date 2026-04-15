"""Djoser/SimpleJWT view subclasses with per-endpoint rate limiting and httpOnly refresh cookies."""

from django.conf import settings
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .cookies import set_refresh_cookie
from .throttles import (
    LoginRateThrottle,
    PasswordResetRateThrottle,
    RefreshRateThrottle,
    RegisterRateThrottle,
)


class ThrottledTokenObtainPairView(TokenObtainPairView):
    """Login: returns access token in body, refresh token as httpOnly cookie."""

    throttle_classes = [LoginRateThrottle]

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK and "refresh" in response.data:
            refresh = response.data.pop("refresh")
            set_refresh_cookie(response, refresh)
        return response


class ThrottledTokenRefreshView(TokenRefreshView):
    """Refresh: reads refresh token from httpOnly cookie, returns access in body."""

    throttle_classes = [RefreshRateThrottle]

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(settings.REFRESH_COOKIE_NAME)
        if not refresh_token:
            return Response(
                {"detail": "Refresh token cookie missing."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        serializer = self.get_serializer(data={"refresh": refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        validated = serializer.validated_data
        response = Response(
            {"access": validated["access"]}, status=status.HTTP_200_OK
        )
        if "refresh" in validated:
            set_refresh_cookie(response, validated["refresh"])
        return response


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
