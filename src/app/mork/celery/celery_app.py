"""Mork celery configuration file."""

import sentry_sdk
from celery import Celery, signals
from sentry_sdk.scrubber import DEFAULT_PII_DENYLIST, EventScrubber

from mork import __version__
from mork.conf import settings

from .probe import LivenessProbe

app = Celery(
    "mork",
    include=[
        "mork.celery.tasks.deletion",
        "mork.celery.tasks.edx",
        "mork.celery.tasks.emailing",
    ],
)
app.steps["worker"].add(LivenessProbe)


@signals.celeryd_init.connect
def init_sentry(**_kwargs):
    """Initialize Sentry SDK on Celery startup."""
    if settings.SENTRY_DSN is not None:
        pii_denylist = DEFAULT_PII_DENYLIST + ["email", "username"]
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            enable_tracing=True,
            traces_sample_rate=settings.SENTRY_CELERY_TRACES_SAMPLE_RATE,
            release=__version__,
            environment=settings.SENTRY_EXECUTION_ENVIRONMENT,
            max_breadcrumbs=50,
            send_default_pii=False,
            event_scrubber=EventScrubber(pii_denylist=pii_denylist),
        )
        sentry_sdk.set_tag("application", "celery")


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("mork.conf:settings", namespace="CELERY")
