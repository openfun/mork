"""Edx database test fixtures."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mork.conf import settings
from mork.edx.database import OpenEdxDB
from mork.edx.factories.base import engine, session
from mork.edx.models.base import Base as EdxBase
from mork.models import Base


@pytest.fixture
def edx_db():
    """"""
    db = OpenEdxDB(engine, session)
    EdxBase.metadata.create_all(engine)
    yield db
    db.session.rollback()
    EdxBase.metadata.drop_all(engine)


@pytest.fixture(scope="session")
def db_engine():
    """Test database engine fixture."""
    engine = create_engine(settings.TEST_DB_URL, echo=False)
    # Create database and tables
    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Test session fixture."""
    # Setup
    #
    # Connect to the database and create a non-ORM transaction. Our connection
    # is bound to the test session.
    connection = db_engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)

    yield session

    # Teardown
    #
    # Rollback everything that happened with the Session above (including
    # explicit commits).
    session.close()
    transaction.rollback()
    connection.close()
