"""API health router.

This module provides endpoints to check the application and database status.
"""

import logging
from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from mork.db import get_session
from mork.db import is_alive as is_db_alive

logger = logging.getLogger(__name__)

router = APIRouter()


class DatabaseStatus(Enum):
    """Possible statuses for the data backend."""

    OK = "ok"
    AWAY = "away"
    ERROR = "error"


class Heartbeat(BaseModel):
    """Status of Warren backends (here, the database)."""

    database: DatabaseStatus

    @property
    def is_alive(self):
        """Checks if all services are operational.

        Returns True if the database is OK.
        """
        if self.database == DatabaseStatus.OK:
            return True
        return False


@router.get("/__lbheartbeat__")
async def lbheartbeat() -> None:
    """Endpoint for the load balancer.

    Returns 200 if the server is working.
    """
    return


@router.get("/__heartbeat__", status_code=status.HTTP_200_OK)
async def heartbeat(
    session: Annotated[Session, Depends(get_session)], response: Response
) -> Heartbeat:
    """Main application health check endpoint.

    Returns 200 if everything is OK, 500 otherwise.
    """
    statuses = Heartbeat(
        database=DatabaseStatus.OK if is_db_alive(session) else DatabaseStatus.ERROR,
    )
    if not statuses.is_alive:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    return statuses
