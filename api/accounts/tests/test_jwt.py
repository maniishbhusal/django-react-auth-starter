"""Tests for JWT authentication endpoints."""

import pytest
from django.conf import settings
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User


@pytest.mark.django_db
class TestJWTCreate:
    """Tests for POST /api/v1/auth/jwt/create/ endpoint."""

    url = "/api/v1/auth/jwt/create/"

    def test_login_success(self, api_client: APIClient, user: User):
        """Login returns access token in body and refresh token as httpOnly cookie."""
        response = api_client.post(
            self.url,
            {"email": user.email, "password": "TestPass123!"},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" not in response.data

        cookie = response.cookies.get(settings.REFRESH_COOKIE_NAME)
        assert cookie is not None
        assert cookie.value
        assert cookie["httponly"]
        assert cookie["samesite"] == settings.REFRESH_COOKIE_SAMESITE
        assert cookie["path"] == settings.REFRESH_COOKIE_PATH

    def test_login_with_wrong_password(self, api_client: APIClient, user: User):
        """Test login fails with wrong password."""
        response = api_client.post(
            self.url,
            {"email": user.email, "password": "WrongPassword123!"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_with_nonexistent_email(self, api_client: APIClient):
        """Test login fails with nonexistent email."""
        response = api_client.post(
            self.url,
            {"email": "nonexistent@example.com", "password": "TestPass123!"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_with_inactive_user(self, api_client: APIClient, inactive_user: User):
        """Test login fails for inactive user."""
        response = api_client.post(
            self.url,
            {"email": inactive_user.email, "password": "TestPass123!"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_without_email(self, api_client: APIClient):
        """Test login fails without email."""
        response = api_client.post(
            self.url,
            {"password": "TestPass123!"},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_without_password(self, api_client: APIClient, user: User):
        """Test login fails without password."""
        response = api_client.post(
            self.url,
            {"email": user.email},
            format="json",
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestJWTRefresh:
    """Tests for POST /api/v1/auth/jwt/refresh/ endpoint."""

    url = "/api/v1/auth/jwt/refresh/"
    login_url = "/api/v1/auth/jwt/create/"

    def test_refresh_token_success(self, api_client: APIClient, user: User):
        """Refresh reads token from cookie, returns new access in body and rotates the cookie."""
        login_response = api_client.post(
            self.login_url,
            {"email": user.email, "password": "TestPass123!"},
            format="json",
        )
        assert login_response.status_code == status.HTTP_200_OK
        # APIClient persists cookies across requests automatically.

        response = api_client.post(self.url, {}, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" not in response.data

        new_cookie = response.cookies.get(settings.REFRESH_COOKIE_NAME)
        assert new_cookie is not None
        assert new_cookie.value
        assert new_cookie["httponly"]

    def test_refresh_with_invalid_token(self, api_client: APIClient):
        """Test refresh fails when cookie value is invalid."""
        api_client.cookies[settings.REFRESH_COOKIE_NAME] = "invalid-token"
        response = api_client.post(self.url, {}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_without_cookie(self, api_client: APIClient):
        """Test refresh fails when no cookie is sent."""
        response = api_client.post(self.url, {}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestJWTVerify:
    """Tests for POST /api/v1/auth/jwt/verify/ endpoint."""

    url = "/api/v1/auth/jwt/verify/"
    login_url = "/api/v1/auth/jwt/create/"

    def test_verify_valid_token(self, api_client: APIClient, user: User):
        """Test verifying a valid access token."""
        login_response = api_client.post(
            self.login_url,
            {"email": user.email, "password": "TestPass123!"},
            format="json",
        )
        access_token = login_response.data["access"]

        response = api_client.post(
            self.url,
            {"token": access_token},
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_verify_invalid_token(self, api_client: APIClient):
        """Test verifying an invalid token fails."""
        response = api_client.post(
            self.url,
            {"token": "invalid-token"},
            format="json",
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_verify_without_token(self, api_client: APIClient):
        """Test verify fails without token."""
        response = api_client.post(self.url, {}, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
