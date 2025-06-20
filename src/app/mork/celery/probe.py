"""Custom liveness and readiness probes for Celery (Mork).

This module allows checking the health and availability of Celery workers
via files on disk.
"""

from pathlib import Path

from celery import bootsteps
from celery.signals import worker_ready, worker_shutdown

# File used for heartbeat (liveness)
HEARTBEAT_FILE = Path("/tmp/worker_heartbeat")  # noqa: S108
# File used for readiness
READINESS_FILE = Path("/tmp/worker_ready")  # noqa: S108


class LivenessProbe(bootsteps.StartStopStep):
    """Celery component that implements a custom liveness probe.

    Creates a heartbeat file regularly to indicate that the worker is alive.
    """

    requires = {"celery.worker.components:Timer"}

    def __init__(self, worker, **kwargs):  # noqa: ARG002
        """Initialize the liveness probe."""
        self.requests = []
        self.tref = None

    def start(self, worker):
        """Start the liveness probe with periodic heartbeat."""
        # Update the heartbeat file every second
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
        """Update the heartbeat file (touch)."""
        HEARTBEAT_FILE.touch()


@worker_ready.connect
def worker_ready(**_):
    """Signal handler: creates the readiness file when the worker is ready."""
    READINESS_FILE.touch()


@worker_shutdown.connect
def worker_shutdown(**_):
    """Signal handler: removes the readiness file when the worker shuts down."""
    READINESS_FILE.unlink(missing_ok=True)
