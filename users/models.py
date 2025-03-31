from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # Add custom fields here in the future
    # Example:
    # organization = models.ForeignKey('organizations.Organization', null=True, blank=True, on_delete=models.SET_NULL)
    # subscription_plan = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(unique=True)

    # Make email the username field for login if desired
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username'] # If email is USERNAME_FIELD, username might still be needed by AbstractUser

    def __str__(self):
        return self.email