"""Main module for Mork API."""

from functools import lru_cache
from typing import Dict, List, Union
from urllib.parse import urlparse

import sentry_sdk
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from mork import __version__
from mork.api.routes import health, tasks
from mork.conf import settings
from mork.database import get_engine


@lru_cache(maxsize=None)
def get_health_check_routes() -> List:
    """Return the health check routes."""
    return [route.path for route in health.router.routes]


def filter_transactions(event: Dict, hint) -> Union[Dict, None]:  # noqa: ARG001
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
            traces_sample_rate=settings.SENTRY_API_TRACES_SAMPLE_RATE,
            release=__version__,
            environment=settings.SENTRY_EXECUTION_ENVIRONMENT,
            max_breadcrumbs=50,
            before_send_transaction=filter_transactions,
        )

    yield
    engine.dispose()


app = FastAPI(lifespan=lifespan)
app.include_router(health.router)
app.include_router(tasks.router)
