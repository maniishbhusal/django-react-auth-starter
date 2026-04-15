"""Account views."""

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .cookies import clear_refresh_cookie
from .throttles import LoginRateThrottle


class LogoutView(APIView):
    """Blacklist the refresh token (read from httpOnly cookie) and clear the cookie.

    Idempotent: always returns 200 and clears the cookie, even if no cookie was
    present or the token was already invalid. Logout should always succeed from
    the user's perspective.
    """

    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        refresh_token = request.COOKIES.get(settings.REFRESH_COOKIE_NAME)

        response = Response(
            {"detail": "Successfully logged out."},
            status=status.HTTP_200_OK,
        )
        clear_refresh_cookie(response)

        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except TokenError:
                pass  # cookie was invalid/expired; we still cleared it client-side

        return response
