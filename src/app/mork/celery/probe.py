"""Mork Celery custom liveness and readiness probes."""

from pathlib import Path

from celery import bootsteps
from celery.signals import worker_ready, worker_shutdown

HEARTBEAT_FILE = Path("/tmp/worker_heartbeat")  # noqa: S108
READINESS_FILE = Path("/tmp/worker_ready")  # noqa: S108


class LivenessProbe(bootsteps.StartStopStep):
    """Celery worker component that implements a liveness probe mechanism."""

    requires = {"celery.worker.components:Timer"}

    def __init__(self, worker, **kwargs):  # noqa: ARG002
        """Initialize the liveness probe."""
        self.requests = []
        self.tref = None

    def start(self, worker):
        """Start the liveness probe with a periodic heartbeat."""
        # Touch the heartbeat file every second
        self.tref = worker.timer.call_repeatedly(
            1.0,
            self.update_heartbeat_file,
            (worker,),
            priority=10,
        )

    def stop(self, worker):  # noqa: ARG002
        """Stop the liveness probe by removing the heartbeat file."""
        HEARTBEAT_FILE.unlink(missing_ok=True)

    def update_heartbeat_file(self, worker):  # noqa: ARG002
        """Update the heartbeat file by touching it."""
        HEARTBEAT_FILE.touch()


@worker_ready.connect
def worker_ready(**_):
    """Signal handler that creates a readiness file when the worker is ready."""
    READINESS_FILE.touch()


@worker_shutdown.connect
def worker_shutdown(**_):
    """Signal handler that removes the readiness file when the worker shuts down."""
    READINESS_FILE.unlink(missing_ok=True)
