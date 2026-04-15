"""Testing settings."""

from .base import *  # noqa: F401, F403

SECRET_KEY = "test-only-secret-key-not-for-production"  # noqa: S105

DEBUG = True

ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]

# Use SQLite for tests
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": str(BASE_DIR / "test_db.sqlite3"),  # noqa: F405
    }
}

# Disable password validators for faster tests
AUTH_PASSWORD_VALIDATORS = []

# Use locmem email backend for tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Effectively disable throttling in tests. Global throttle classes are removed;
# scoped rates are kept at a high ceiling because per-view custom throttles
# (LoginRateThrottle etc.) still read their rate by scope name at instantiation.
REST_FRAMEWORK["DEFAULT_THROTTLE_CLASSES"] = []  # noqa: F405
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {  # noqa: F405
    "login": "10000/minute",
    "register": "10000/minute",
    "password_reset": "10000/minute",
}

# Faster password hashing for tests
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# Disable activation email requirement for testing
DJOSER["SEND_ACTIVATION_EMAIL"] = False  # noqa: F405

# Refresh cookie: test client is HTTP
REFRESH_COOKIE_SECURE = False
