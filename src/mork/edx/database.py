"""Mork database connection."""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mork.conf import settings

logger = logging.getLogger(__name__)


class OpenEdxDB:
    """Class to connect to the Open edX database."""

    session = None

    def __init__(self, engine=None, session=None):
        """Initialize SqlAlchemy engine and session."""
        if engine is not None:
            self.engine = engine
        else:
            self.engine = create_engine(
                settings.EDX_DB_URL, echo=settings.EDX_DB_DEBUG, pool_pre_ping=True
            )
        if session is not None:
            self.session = session
        else:
            self.session = Session(self.engine)
