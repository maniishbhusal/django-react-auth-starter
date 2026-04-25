"""Account serializers."""

from typing import Any

from django.utils import timezone
from djoser.serializers import (
    UserCreatePasswordRetypeSerializer as BaseUserCreateSerializer,
)
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import User


class UserCreateSerializer(BaseUserCreateSerializer):
    """Serializer for user registration with password confirmation."""

    full_name = serializers.CharField(required=True, allow_blank=False)
    agreed_to_terms = serializers.BooleanField(required=True)

    class Meta(BaseUserCreateSerializer.Meta):
        """Meta options."""

        model = User
        fields = tuple(BaseUserCreateSerializer.Meta.fields) + (
            "full_name",
            "agreed_to_terms",
        )

    def get_fields(self):
        """Drop default UniqueValidator on email; we handle duplicates ourselves."""
        fields = super().get_fields()
        if "email" in fields:
            fields["email"].validators = [
                v
                for v in fields["email"].validators
                if not isinstance(v, UniqueValidator)
            ]
        return fields

    def validate_email(self, value: str) -> str:
        """Reject duplicates only against active (verified) rows."""
        normalized = value.lower().strip()
        existing = User.objects.filter(email__iexact=normalized).first()
        if existing is not None and existing.is_active:
            raise serializers.ValidationError(
                "user with this email already exists."
            )
        return normalized

    def validate_agreed_to_terms(self, value: bool) -> bool:
        """Ensure user agrees to terms of service."""
        if not value:
            raise serializers.ValidationError(
                "You must agree to the Terms of Service and Privacy Policy."
            )
        return value

    def validate_full_name(self, value: str) -> str:
        """Ensure full name is provided."""
        if not value or not value.strip():
            raise serializers.ValidationError("Full name is required.")
        return value.strip()

    def create(self, validated_data: dict[str, Any]) -> User:
        """Create a new user, or trigger an activation re-send for an unverified row."""
        email = validated_data["email"]
        existing = User.objects.filter(
            email__iexact=email, is_active=False
        ).first()
        if existing is not None:
            # SECURITY: Do NOT mutate the row. An unauthenticated caller has not
            # proven control of this email, so overwriting the password here would
            # let an attacker hijack a pending account when the real owner clicks
            # the activation email they were already expecting. Returning the row
            # unchanged still triggers djoser's activation email on save, which
            # is functionally a re-send for the original registrant.
            return existing

        full_name = validated_data.pop("full_name", "")
        agreed_to_terms = validated_data.pop("agreed_to_terms", False)
        user = super().create(validated_data)
        user.full_name = full_name
        user.agreed_to_terms = agreed_to_terms
        user.agreed_at = timezone.now()
        user.save(update_fields=["full_name", "agreed_to_terms", "agreed_at"])
        return user


class UserSerializer(BaseUserSerializer):
    """Serializer for user data."""

    class Meta(BaseUserSerializer.Meta):
        """Meta options."""

        model = User
        fields = (
            "id",
            "email",
            "full_name",
            "agreed_to_terms",
            "agreed_at",
            "date_joined",
        )
        read_only_fields = (
            "id",
            "email",
            "agreed_to_terms",
            "agreed_at",
            "date_joined",
        )
