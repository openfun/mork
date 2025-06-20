"""Main Mork API module.

This module initializes the FastAPI application, configures Sentry for error handling,
mounts health routes and API version 1.
"""

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
    """Returns health check routes.

    Useful for ignoring these routes in Sentry.
    """
    return [route.path for route in health_router.routes]


def filter_transactions(event: dict, hint) -> dict | None:  # noqa: ARG001
    """Filters transactions for Sentry.

    Ignores health check requests if configured.
    """
    url = urlparse(event["request"]["url"])

    if settings.SENTRY_IGNORE_HEALTH_CHECKS and url.path in get_health_check_routes():
        return None

    return event


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: ARG001
    """Application lifecycle management.

    Initializes Sentry if configured and manages database connection.
    """
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
        sentry_sdk.set_tag("application", "api")

    yield
    engine.dispose()


# Create the main FastAPI application
app = FastAPI(title="Mork", lifespan=lifespan)

# Add health check routes
app.include_router(health_router)

# Mount API version 1 under the /v1 prefix
app.mount("/v1", v1)
