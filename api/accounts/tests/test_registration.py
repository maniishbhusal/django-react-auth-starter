"""Tests for user registration endpoint."""

import pytest
from django.core import mail
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User


@pytest.mark.django_db
class TestUserRegistration:
    """Tests for POST /api/v1/auth/users/ endpoint."""

    url = "/api/v1/auth/users/"

    def test_register_user_success(self, api_client: APIClient, user_data: dict):
        """Test successful user registration."""
        response = api_client.post(self.url, user_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["email"] == user_data["email"]
        assert "password" not in response.data

        # Verify user was created in database
        user = User.objects.get(email=user_data["email"])
        assert user.full_name == user_data["full_name"]
        assert user.agreed_to_terms is True

    def test_register_without_email(self, api_client: APIClient, user_data: dict):
        """Test registration fails without email."""
        del user_data["email"]
        response = api_client.post(self.url, user_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_register_with_invalid_email(self, api_client: APIClient, user_data: dict):
        """Test registration fails with invalid email."""
        user_data["email"] = "invalid-email"
        response = api_client.post(self.url, user_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_register_with_duplicate_active_email(
        self, api_client: APIClient, user_data: dict, user: User
    ):
        """Duplicate signup against an active (verified) user is rejected."""
        user_data["email"] = user.email
        user_data["username"] = "newusername"
        response = api_client.post(self.url, user_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data
        assert response.data["email"][0] == "user with this email already exists."

    def test_register_reactivates_inactive_user(
        self, api_client: APIClient, user_data: dict, inactive_user: User
    ):
        """Duplicate signup against an unverified row reactivates it in place."""
        original_id = inactive_user.id
        original_password_hash = inactive_user.password

        user_data["email"] = inactive_user.email
        user_data["username"] = "freshusername"
        user_data["full_name"] = "Reactivated Name"
        user_data["password"] = "BrandNewPass456!"
        user_data["re_password"] = "BrandNewPass456!"

        mail.outbox = []
        response = api_client.post(self.url, user_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

        refreshed = User.objects.get(email__iexact=inactive_user.email)
        assert refreshed.id == original_id
        assert refreshed.is_active is False
        assert refreshed.full_name == "Reactivated Name"
        assert refreshed.password != original_password_hash
        assert refreshed.check_password("BrandNewPass456!")
        assert refreshed.agreed_to_terms is True
        assert refreshed.agreed_at is not None

        assert len(mail.outbox) == 1
        assert inactive_user.email in mail.outbox[0].to

    def test_register_without_password(self, api_client: APIClient, user_data: dict):
        """Test registration fails without password."""
        del user_data["password"]
        response = api_client.post(self.url, user_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data

    def test_register_with_mismatched_passwords(
        self, api_client: APIClient, user_data: dict
    ):
        """Test registration fails when passwords don't match."""
        user_data["re_password"] = "DifferentPass123!"
        response = api_client.post(self.url, user_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data

    def test_register_without_full_name(self, api_client: APIClient, user_data: dict):
        """Test registration fails without full name."""
        user_data["full_name"] = ""
        response = api_client.post(self.url, user_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "full_name" in response.data

    def test_register_with_whitespace_full_name(
        self, api_client: APIClient, user_data: dict
    ):
        """Test registration fails with whitespace-only full name."""
        user_data["full_name"] = "   "
        response = api_client.post(self.url, user_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "full_name" in response.data

    def test_register_without_agreed_to_terms(
        self, api_client: APIClient, user_data: dict
    ):
        """Test registration fails without agreeing to terms."""
        user_data["agreed_to_terms"] = False
        response = api_client.post(self.url, user_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "agreed_to_terms" in response.data

    def test_register_without_username(self, api_client: APIClient, user_data: dict):
        """Test registration fails without username."""
        del user_data["username"]
        response = api_client.post(self.url, user_data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.data

    def test_full_name_is_trimmed(self, api_client: APIClient, user_data: dict):
        """Test full name is trimmed of leading/trailing whitespace."""
        user_data["full_name"] = "  John Doe  "
        response = api_client.post(self.url, user_data, format="json")
        assert response.status_code == status.HTTP_201_CREATED

        user = User.objects.get(email=user_data["email"])
        assert user.full_name == "John Doe"
