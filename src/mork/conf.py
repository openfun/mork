"""Configurations for Mork."""

import io
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Pydantic model for Mork's global environment & configuration settings."""

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        env_file_encoding=getattr(io, "LOCALE_ENCODING", "utf-8"),
        env_nested_delimiter="__",
        env_prefix="MORK_",
        extra="ignore",
    )

    # Mork server
    API_SERVER_PROTOCOL: str = "http"
    API_SERVER_HOST: str = "localhost"
    API_SERVER_PORT: int = 8100
    API_KEYS: list[str] = ["APIKeyToBeChanged"]

    # Celery
    broker_url: str = Field("redis://redis:6379/0", alias="MORK_CELERY_BROKER_URL")
    result_backend: str = Field(
        "redis://redis:6379/0", alias="MORK_CELERY_RESULT_BACKEND"
    )
    broker_transport_options: dict = Field(
        {}, alias="MORK_CELERY_BROKER_TRANSPORT_OPTIONS"
    )
    task_default_queue: str = Field("celery", alias="MORK_CELERY_TASK_DEFAULT_QUEUE")

    # Sentry
    SENTRY_DSN: Optional[str] = None
    SENTRY_EXECUTION_ENVIRONMENT: str = "development"
    SENTRY_API_TRACES_SAMPLE_RATE: float = 1.0
    SENTRY_IGNORE_HEALTH_CHECKS: bool = False

    @property
    def SERVER_URL(self) -> str:
        """Get the full server URL."""
        return f"{self.API_SERVER_PROTOCOL}://{self.API_SERVER_HOST}:{self.API_SERVER_PORT}"


settings = Settings()
