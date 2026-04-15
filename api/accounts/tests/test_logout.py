"""Tests for logout endpoint."""

import pytest
from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from conftest import USER_PASSWORD


@pytest.mark.django_db
class TestLogoutView:
    """Tests for POST /api/v1/auth/logout/ endpoint."""

    url = "/api/v1/auth/logout/"
    login_url = "/api/v1/auth/jwt/create/"
    refresh_url = "/api/v1/auth/jwt/refresh/"

    def test_logout_success(self, api_client: APIClient, user: User):
        """Logout reads refresh from cookie, blacklists it, and clears the cookie."""
        login_response = api_client.post(
            self.login_url,
            {"email": user.email, "password": USER_PASSWORD},
            format="json",
        )
        assert login_response.status_code == status.HTTP_200_OK
        refresh_token = login_response.cookies[settings.REFRESH_COOKIE_NAME].value

        response = api_client.post(self.url, {}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Successfully logged out."

        cleared = response.cookies.get(settings.REFRESH_COOKIE_NAME)
        assert cleared is not None
        assert cleared.value == ""

        # The blacklisted token should no longer be usable for refresh.
        api_client.cookies[settings.REFRESH_COOKIE_NAME] = refresh_token
        refresh_response = api_client.post(self.refresh_url, {}, format="json")
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_without_cookie_is_idempotent(self, api_client: APIClient):
        """Logout with no cookie still returns 200 (idempotent UX)."""
        response = api_client.post(self.url, {}, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Successfully logged out."

    def test_logout_with_invalid_cookie_is_idempotent(self, api_client: APIClient):
        """Logout with an invalid cookie still returns 200 and clears the cookie."""
        api_client.cookies[settings.REFRESH_COOKIE_NAME] = "invalid-token"
        response = api_client.post(self.url, {}, format="json")
        assert response.status_code == status.HTTP_200_OK

        cleared = response.cookies.get(settings.REFRESH_COOKIE_NAME)
        assert cleared is not None
        assert cleared.value == ""
