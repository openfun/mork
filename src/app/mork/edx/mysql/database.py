"""Mork edx MySQL database connection."""

import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mork.conf import settings

logger = logging.getLogger(__name__)


class OpenEdxMySQLDB:
    """Class to connect to the Open edX MySQL database."""

    session = None

    def __init__(self, engine=None, session=None):
        """Instantiate SQLAlchemy engine and session."""
        if engine is not None:
            self.engine = engine
        else:
            self.engine = create_engine(
                settings.EDX_MYSQL_DB_URL,
                echo=settings.EDX_MYSQL_DB_DEBUG,
                pool_pre_ping=True,
            )
        if session is not None:
            self.session = session
        else:
            self.session = Session(self.engine)
