"""Mork database connection."""

import logging
from threading import Lock
from typing import Generator, Optional

from pydantic import PostgresDsn
from sqlalchemy import Engine as SAEngine
from sqlalchemy import NullPool, create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session as SASession

from mork.conf import settings

logger = logging.getLogger(__name__)


class MorkDB:
    """Class to connect to the Mork database.

    This class is used by Celery workers to start a new engine and session per process.
    """

    session = None

    def __init__(self):
        """Initialize SqlAlchemy engine and session."""
        # Disable pooling as SQLAlchemy connections cannot be shared accross processes,
        # and Celery forks processes by default
        self.engine = create_engine(
            settings.DB_URL, echo=settings.DB_DEBUG, poolclass=NullPool
        )
        self.session = SASession(self.engine)


class Singleton(type):
    """Thread-safe singleton pattern metaclass."""

    _instances: dict = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        """Store instances in a private class property."""
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class Engine(metaclass=Singleton):
    """Database engine singleton used by the API to connect to the Mork database."""

    _engine: Optional[SAEngine] = None

    def get_engine(self, url: PostgresDsn, echo: bool = False) -> SAEngine:
        """Get created engine or create a new one."""
        if self._engine is None:
            logger.debug("Create a new engine")
            self._engine = create_engine(str(url), echo=echo)
        logger.debug("Getting database engine %s", self._engine)
        return self._engine


def get_engine() -> SAEngine:
    """Get database engine."""
    return Engine().get_engine(url=settings.DB_URL, echo=settings.DB_DEBUG)


def get_session() -> Generator[SASession, None, None]:
    """Get database session."""
    with SASession(bind=get_engine()) as session:
        logger.debug("Getting session %s", session)
        yield session
        logger.debug("Closing session %s", session)


def is_alive(session: SASession) -> bool:
    """Check if database connection is alive."""
    try:
        session.execute(text("SELECT 1 as is_alive"))
        return True
    except OperationalError as err:
        logger.debug("Exception: %s", err)
        return False
