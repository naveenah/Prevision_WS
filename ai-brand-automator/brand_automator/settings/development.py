"""
Development settings
"""
from .base import *

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "*.localhost"]

# Development database (SQLite for quick setup)
if config("USE_SQLITE", default=False, cast=bool):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Django Debug Toolbar
if "django_debug_toolbar" in INSTALLED_APPS:
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = ["127.0.0.1"]

# Email backend (console for development)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# CORS - allow all origins in development
CORS_ALLOW_ALL_ORIGINS = True
