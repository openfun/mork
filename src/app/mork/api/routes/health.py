"""API routes related to application health checking."""

import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/__lbheartbeat__")
async def lbheartbeat() -> None:
    """Load balancer heartbeat.

    Return a 200 when the server is running.
    """
    return
