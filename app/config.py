"""Central configuration, read from environment variables."""
import os
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()


class Config:
    ENV = os.environ.get("FLASK_ENV", "production")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    DATABASE_URL = os.environ.get("DATABASE_URL")
    SITE_URL = os.environ.get("SITE_URL", "").rstrip("/")  # e.g. https://yourcompany.com
    MAX_CONTENT_LENGTH = 3 * 1024 * 1024  # request cap; custom thumbnails are limited to 1 MB
    SEND_FILE_MAX_AGE_DEFAULT = timedelta(hours=1)
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = ENV == "production"

    @classmethod
    def validate(cls):
        """Fail fast in production if required settings are missing."""
        if cls.ENV == "production":
            missing = [n for n in ("SECRET_KEY", "DATABASE_URL") if not getattr(cls, n)]
            if missing:
                raise RuntimeError("Set these environment variables in production: " + ", ".join(missing))
