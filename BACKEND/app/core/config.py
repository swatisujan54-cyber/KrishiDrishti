"""Application configuration loaded from environment variables / .env file.

All tunable settings live here so nothing is hard-coded across the codebase.
To override any default, create a ``.env`` file (see ``.env.example``) or set
the corresponding environment variable.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central settings for the KrishiDrishti backend.

    Values are read from environment variables first, then from a local
    ``.env`` file, falling back to the defaults below.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ---- Application ----
    APP_NAME: str = "KrishiDrishti API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api"

    # ---- Database ----
    # SQLite for development; switch to a postgresql URL for production.
    DATABASE_URL: str = "sqlite:///./data/krishidrishti.db"

    # ---- Security ----
    SECRET_KEY: str = "change-me-to-a-long-random-secret-string"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # ---- CORS ----
    # Comma-separated list in the env var; parsed via the property below.
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://localhost:8080"

    # ---- Image upload ----
    UPLOAD_DIR: str = "data/uploads"
    MAX_IMAGE_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB
    ALLOWED_IMAGE_FORMATS: str = "JPEG,PNG"

    # ---- Prediction / AI ----
    # Leave empty to use the mock predictor during development.
    MODEL_PATH: str = ""
    LABELS_PATH: str = "ml/labels.json"
    # Stored as "WIDTH,HEIGHT" in the env var.
    IMAGE_SIZE: str = "224,224"
    PREDICTION_CONFIDENCE_THRESHOLD: float = 0.5
    PREDICTION_TOP_K: int = 3

    # ---- Languages ----
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: str = "en,hi"

    # ---- Pagination ----
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # ------------------------------------------------------------------ #
    # Helper properties that turn the comma-separated strings into lists.  #
    # ------------------------------------------------------------------ #

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def allowed_image_formats_list(self) -> list[str]:
        return [f.strip().upper() for f in self.ALLOWED_IMAGE_FORMATS.split(",") if f.strip()]

    @property
    def supported_languages_list(self) -> list[str]:
        return [l.strip().lower() for l in self.SUPPORTED_LANGUAGES.split(",") if l.strip()]

    @property
    def image_size_tuple(self) -> tuple[int, int]:
        parts = [int(p.strip()) for p in self.IMAGE_SIZE.split(",")]
        if len(parts) != 2:
            return (224, 224)
        return (parts[0], parts[1])


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (created once per process)."""
    return Settings()


# Convenient module-level singleton imported throughout the app.
settings = get_settings()
