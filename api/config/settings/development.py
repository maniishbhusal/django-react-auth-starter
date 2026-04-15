"""Development settings."""

from .base import *  # noqa: F401, F403

if not SECRET_KEY:  # noqa: F405
    SECRET_KEY = "django-insecure-dev-only-do-not-use-in-production"

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

# Use SQLite for local development
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR / "db.sqlite3"),
    }
}

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Email: Use console backend for local development (prints to terminal)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Refresh cookie: localhost is HTTP, so Secure must be False
REFRESH_COOKIE_SECURE = False
