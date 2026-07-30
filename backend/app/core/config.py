"""
config.py
---------
Centralised configuration using pydantic-settings.

All environment variables are read ONCE from backend/.env at import
time, validated against their declared types, and exposed through the
module-level `settings` singleton.

Usage anywhere in the backend:
    from app.core.config import settings
    print(settings.MISTRAL_API_KEY)
"""

import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables / .env file.

    Every field has a type annotation so pydantic auto-validates on startup.
    If a required variable (no default) is missing, the app will refuse to
    start and print a clear error — far better than a cryptic runtime crash.
    """

    # ── Application Metadata ──────────────────────────────────────
    APP_NAME: str = "AI Meeting Summarizer API"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = "development"    # "development" | "staging" | "production"
    DEBUG: bool = True

    # ── AI Service Keys ───────────────────────────────────────────
    MISTRAL_API_KEY: str            # Required — no default
    HF_TOKEN: str = ""              # Optional — used for HuggingFace embeddings

    # ── Whisper Model Configuration ───────────────────────────────
    WHISPER_MODEL: str = "small"    # tiny | small | medium | large-v3
    WHISPER_DEVICE: str = "cpu"     # cpu | cuda

    # ── File Storage Paths ────────────────────────────────────────
    # Stored as relative paths in .env; resolved to absolute below.
    UPLOADS_DIR: str = "backend/uploads"
    OUTPUTS_DIR: str = "backend/outputs"

    # ── CORS Configuration ────────────────────────────────────────
    # Accepts either a comma-separated string ("http://a.com,http://b.com")
    # or a JSON list ("[\"http://a.com\"]") from the .env file.
    # Use ["*"] in development; lock down to Flutter app URL in production.
    ALLOWED_ORIGINS: Union[List[str], str] = ["*"]

    # ── pydantic-settings config ──────────────────────────────────
    model_config = SettingsConfigDict(
        env_file="backend/.env",
        env_file_encoding="utf-8",
        case_sensitive=True,        # Env vars must match case exactly
        extra="ignore",             # Silently ignore unknown .env keys
    )

    # ── Validators ────────────────────────────────────────────────

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        """
        Allows ALLOWED_ORIGINS to be written in .env as either:
          ALLOWED_ORIGINS=*
          ALLOWED_ORIGINS=http://localhost:3000,http://myapp.com
        and converts it into a proper Python list.
        """
        if isinstance(v, str):
            # Split comma-separated string into a list
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("UPLOADS_DIR", "OUTPUTS_DIR", mode="after")
    @classmethod
    def resolve_paths(cls, v):
        """
        Convert relative paths to absolute paths anchored at the
        project root (two levels up from this file: backend/app/core/).
        This ensures the paths work correctly regardless of the
        current working directory when uvicorn is started.
        """
        if not os.path.isabs(v):
            project_root = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", "..")
            )
            return os.path.join(project_root, v)
        return v


# ─────────────────────────────────────────────────────────────────
# SINGLETON
#
# Instantiated once at module import time.
# Import and use this object everywhere — never instantiate Settings()
# again elsewhere.
# ─────────────────────────────────────────────────────────────────
settings = Settings()
