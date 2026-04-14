"""Tests for logout endpoint."""

import pytest
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
        """Test successful logout blacklists refresh token."""
        login_response = api_client.post(
            self.login_url,
            {"email": user.email, "password": USER_PASSWORD},
            format="json",
        )
        assert login_response.status_code == status.HTTP_200_OK
        access_token = login_response.data["access"]
        refresh_token = login_response.data["refresh"]

        response = api_client.post(
            self.url,
            {"refresh": refresh_token},
            format="json",
            HTTP_AUTHORIZATION=f"Bearer {access_token}",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["detail"] == "Successfully logged out."

        refresh_response = api_client.post(
            self.refresh_url,
            {"refresh": refresh_token},
            format="json",
        )
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_logout_without_refresh(self, authenticated_client: APIClient):
        """Test logout fails when refresh token is missing."""
        response = authenticated_client.post(self.url, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Refresh token is required."

    def test_logout_with_invalid_token(self, authenticated_client: APIClient):
        """Test logout fails with invalid or expired refresh token."""
        response = authenticated_client.post(
            self.url,
            {"refresh": "invalid-token"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["detail"] == "Invalid or expired token."

    def test_logout_without_bearer_still_blacklists(
        self, api_client: APIClient, user: User
    ):
        """Logout works without a Bearer access token — the refresh token is the capability.

        A user whose access token is expired or stolen must still be able to
        invalidate their refresh token.
        """
        login_response = api_client.post(
            self.login_url,
            {"email": user.email, "password": USER_PASSWORD},
            format="json",
        )
        assert login_response.status_code == status.HTTP_200_OK
        refresh_token = login_response.data["refresh"]

        response = api_client.post(
            self.url,
            {"refresh": refresh_token},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

        refresh_response = api_client.post(
            self.refresh_url,
            {"refresh": refresh_token},
            format="json",
        )
        assert refresh_response.status_code == status.HTTP_401_UNAUTHORIZED
