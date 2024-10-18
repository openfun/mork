"""Configurations for Mork."""

import io
from datetime import timedelta
from pathlib import Path
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

    # Warning task configuration
    WARNING_PERIOD: timedelta = "P3Y30D"

    # Deletion task configuration
    DELETION_PERIOD: timedelta = "P3Y"
    DELETE_MAX_RETRIES: int = 3

    # Edx forum configuration
    EDX_FORUM_PLACEHOLDER_USER_ID: int = 1234

    # API Root path
    # (used at least by everything that is alembic-configuration-related)
    ROOT_PATH: Path = Path(__file__).parent

    # Alembic
    ALEMBIC_CFG_PATH: Path = ROOT_PATH / "alembic.ini"

    # Static path
    STATIC_PATH: Path = ROOT_PATH / "static"

    # Mork database
    DB_ENGINE: str = "postgresql+psycopg2"
    DB_HOST: str = "postgresql"
    DB_NAME: str = "mork-db"
    DB_USER: str = "fun"
    DB_PASSWORD: str = "pass"
    DB_PORT: int = 5432
    DB_DEBUG: bool = False
    TEST_DB_NAME: str = "test-mork-db"

    # EDX MySQL database
    EDX_MYSQL_DB_ENGINE: str = "mysql+pymysql"
    EDX_MYSQL_DB_HOST: str = "mysql"
    EDX_MYSQL_DB_NAME: str = "edxapp"
    EDX_MYSQL_DB_USER: str = "edxapp"
    EDX_MYSQL_DB_PASSWORD: str = "password"
    EDX_MYSQL_DB_PORT: int = 3306
    EDX_MYSQL_DB_DEBUG: bool = False
    EDX_MYSQL_QUERY_BATCH_SIZE: int = 1000

    # EDX MongoDB database
    EDX_MONGO_DB_ENGINE: str = "mongodb"
    EDX_MONGO_DB_HOST: str = "mongo"
    EDX_MONGO_DB_NAME: str = "cs_comments_service"
    EDX_MONGO_DB_USER: str = "cs_comments_service"
    EDX_MONGO_DB_PASSWORD: str = "password"
    EDX_MONGO_DB_PORT: int = 27017
    EDX_MONGO_DB_DEBUG: bool = False

    # Emails
    EMAIL_HOST: str = "mailcatcher"
    EMAIL_HOST_USER: str = ""
    EMAIL_HOST_PASSWORD: str = ""
    EMAIL_PORT: int = 1025
    EMAIL_USE_TLS: bool = False
    EMAIL_FROM: str = ""
    EMAIL_RATE_LIMIT: str = "100/m"
    EMAIL_MAX_RETRIES: int = 3
    EMAIL_SITE_NAME: str = ""
    EMAIL_SITE_BASE_URL: str = ""
    EMAIL_SITE_LOGIN_URL: str = ""

    # Celery
    broker_url: str = Field("redis://redis:6379/0", alias="MORK_CELERY_BROKER_URL")
    broker_transport_options: dict = Field(
        {}, alias="MORK_CELERY_BROKER_TRANSPORT_OPTIONS"
    )
    result_backend: str = Field(
        "redis://redis:6379/0", alias="MORK_CELERY_RESULT_BACKEND"
    )
    result_backend_transport_options: dict = Field(
        {}, alias="MORK_CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS"
    )
    task_default_queue: str = Field("celery", alias="MORK_CELERY_TASK_DEFAULT_QUEUE")

    # Sentry
    SENTRY_DSN: Optional[str] = None
    SENTRY_EXECUTION_ENVIRONMENT: str = "development"
    SENTRY_API_TRACES_SAMPLE_RATE: float = 1.0
    SENTRY_IGNORE_HEALTH_CHECKS: bool = False

    @property
    def DB_URL(self) -> str:
        """Get the Mork database URL as required by SQLAlchemy."""
        return (
            f"{self.DB_ENGINE}://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}/{self.DB_NAME}"
        )

    @property
    def TEST_DB_URL(self) -> str:
        """Get the test database URL as required by SQLAlchemy."""
        return (
            f"{self.DB_ENGINE}://"
            f"{self.DB_USER}:{self.DB_PASSWORD}@"
            f"{self.DB_HOST}/{self.TEST_DB_NAME}"
        )

    @property
    def EDX_MYSQL_DB_URL(self) -> str:
        """Get the edx MySQL database URL as required by SQLAlchemy."""
        return (
            f"{self.EDX_MYSQL_DB_ENGINE}://"
            f"{self.EDX_MYSQL_DB_USER}:{self.EDX_MYSQL_DB_PASSWORD}@"
            f"{self.EDX_MYSQL_DB_HOST}/{self.EDX_MYSQL_DB_NAME}"
        )

    @property
    def EDX_MONGO_DB_URL(self) -> str:
        """Get the edx database URL as required by SQLAlchemy."""
        return (
            f"{self.EDX_MONGO_DB_ENGINE}://"
            f"{self.EDX_MONGO_DB_USER}:{self.EDX_MONGO_DB_PASSWORD}@"
            f"{self.EDX_MONGO_DB_HOST}/{self.EDX_MONGO_DB_NAME}"
        )

    @property
    def SERVER_URL(self) -> str:
        """Get the full server URL."""
        return f"{self.API_SERVER_PROTOCOL}://{self.API_SERVER_HOST}:{self.API_SERVER_PORT}"


settings = Settings()
