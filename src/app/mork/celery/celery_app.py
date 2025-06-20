"""Celery configuration file for Mork.

This module initializes the Celery application, configures Sentry for error handling,
and adds custom liveness probes.
"""

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


def before_send(event, hint):  # noqa: ARG001
    """Removes user email from events sent to Sentry.

    Filters Sarbacane URLs to avoid transmitting sensitive data.
    """
    if not event.get("breadcrumbs"):
        return event

    for breadcrumb in event["breadcrumbs"].get("values", []):
        data = breadcrumb.get("data", {})
        url = data.get("url", "")

        # Removes user email from Sarbacane URLs
        for endpoint in ["/contacts", "/unsubscribers", "/complaints"]:
            if endpoint in url:
                data["url"] = url.replace(url.split(f"{endpoint}")[-1], "[Filtered]")
                breadcrumb["data"] = data

    return event


@signals.celeryd_init.connect
def init_sentry(**_kwargs):
    """Initializes the Sentry SDK when the Celery worker starts.

    Configures PII filtering and execution environment.
    """
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
            event_scrubber=EventScrubber(pii_denylist=pii_denylist, recursive=True),
            before_send=before_send,
        )
        sentry_sdk.set_tag("application", "celery")


# Using a string here avoids serializing the configuration object in subprocesses.
# - namespace='CELERY' means that all celery-related configuration keys
#   must have the `CELERY_` prefix.
app.config_from_object("mork.conf:settings", namespace="CELERY")
