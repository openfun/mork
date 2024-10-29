"""Main module for Mork API."""

from functools import lru_cache
from urllib.parse import urlparse

import sentry_sdk
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration

from mork import __version__
from mork.api.health import router as health_router
from mork.api.v1 import app as v1
from mork.conf import settings
from mork.db import get_engine


@lru_cache(maxsize=None)
def get_health_check_routes() -> list:
    """Return the health check routes."""
    return [route.path for route in health_router.routes]


def filter_transactions(event: dict, hint) -> dict | None:  # noqa: ARG001
    """Filter transactions for Sentry."""
    url = urlparse(event["request"]["url"])

    if settings.SENTRY_IGNORE_HEALTH_CHECKS and url.path in get_health_check_routes():
        return None

    return event


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Application life span."""
    engine = get_engine()

    # Sentry
    if settings.SENTRY_DSN is not None:
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            enable_tracing=True,
            traces_sample_rate=settings.SENTRY_API_TRACES_SAMPLE_RATE,
            release=__version__,
            environment=settings.SENTRY_EXECUTION_ENVIRONMENT,
            max_breadcrumbs=50,
            before_send_transaction=filter_transactions,
            integrations=[
                StarletteIntegration(),
                FastApiIntegration(),
            ],
        )

    yield
    engine.dispose()


app = FastAPI(title="Mork", lifespan=lifespan)

# Health checks
app.include_router(health_router)

# Mount v1 API
app.mount("/v1", v1)
