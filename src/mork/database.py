"""Mork database connection."""

import logging

from sqlalchemy import NullPool, create_engine
from sqlalchemy.orm import Session

from mork.conf import settings

logger = logging.getLogger(__name__)


class MorkDB:
    """Class to connect to the Mork database."""

    session = None

    def __init__(self):
        """Initialize SqlAlchemy engine and session."""
        # Disable pooling as SQLAlchemy connections cannot be shared accross processes,
        # and Celery forks processes by default
        self.engine = create_engine(
            settings.DB_URL, echo=settings.DB_DEBUG, poolclass=NullPool
        )
        self.session = Session(self.engine)
