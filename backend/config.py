from functools import lru_cache
import logging
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    DATABASE_URL: str = Field(..., description="PostgreSQL SQLAlchemy connection URL")
    BASE_URL: str = Field(
        default="http://localhost:8000",
        description="Public base URL used to build tracking pixel links",
    )
    ENVIRONMENT: Literal["development", "testing", "production"] = Field(
        default="development",
        description="Runtime environment",
    )
    # Comma-separated list of allowed CORS origins. Empty = CORS middleware disabled.
    CORS_ORIGINS: str = Field(
        default="",
        description="Optional comma-separated CORS origins for the React dashboard",
    )
    DB_POOL_SIZE: int = Field(default=5, ge=1, le=50)
    DB_MAX_OVERFLOW: int = Field(default=10, ge=0, le=100)
    DB_POOL_RECYCLE: int = Field(default=1800, ge=60, le=7200)
    LOG_LEVEL: str = Field(default="INFO")

    @field_validator("DATABASE_URL")
    @classmethod
    def validate_database_url(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("DATABASE_URL must not be empty")
        if not (
            value.startswith("postgresql://")
            or value.startswith("postgresql+psycopg2://")
            or value.startswith("postgres://")
        ):
            raise ValueError(
                "DATABASE_URL must be a PostgreSQL SQLAlchemy connection URL"
            )
        return value

    @field_validator("BASE_URL")
    @classmethod
    def validate_base_url(cls, value: str) -> str:
        value = value.strip().rstrip("/")
        if not value:
            raise ValueError("BASE_URL must not be empty")
        if not (
            value.startswith("http://")
            or value.startswith("https://")
        ):
            raise ValueError("BASE_URL must start with http:// or https://")
        return value

    @field_validator("LOG_LEVEL")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        level = value.strip().upper()
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if level not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of: {', '.join(sorted(allowed))}")
        return level

    def cors_origin_list(self) -> list[str]:
        if not self.CORS_ORIGINS.strip():
            return []
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    def build_tracking_url(self, tracking_token: str) -> str:
        token = (tracking_token or "").strip()
        return f"{self.BASE_URL}/track/open/{token}"

    def safe_db_host_hint(self) -> str:
        """Return a non-secret hint for logs (scheme + host only when possible)."""
        raw = self.DATABASE_URL
        try:
            without_scheme = raw.split("://", 1)[1]
            host_part = without_scheme.split("@")[-1]
            return host_part.split("/")[0]
        except Exception:
            return "configured"


@lru_cache
def get_settings() -> Settings:
    return Settings()


def configure_logging() -> None:
    settings = get_settings()
    root = logging.getLogger()
    if not root.handlers:
        logging.basicConfig(
            level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
            format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        )
    else:
        root.setLevel(getattr(logging, settings.LOG_LEVEL, logging.INFO))
