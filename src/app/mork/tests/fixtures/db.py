"""Edx database test fixtures."""

import mongomock
import pytest
from mongoengine import connect, disconnect
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SASession

from mork.conf import settings
from mork.edx.mysql.database import OpenEdxMySQLDB
from mork.edx.mysql.factories.base import Session, engine
from mork.edx.mysql.models.base import Base as EdxBase
from mork.models.tasks import Base


@pytest.fixture
def edx_mysql_db():
    """Test edx MySQL database fixture."""
    Session.configure(bind=engine)
    db = OpenEdxMySQLDB(engine, Session)
    EdxBase.metadata.create_all(engine)
    yield db
    db.session.rollback()
    EdxBase.metadata.drop_all(engine)


@pytest.fixture
def edx_mongo_db():
    """Test MongDB database fixture."""
    connect(
        db=settings.EDX_MONGO_DB_NAME,
        host=settings.EDX_MONGO_DB_HOST,
        mongo_client_class=mongomock.MongoClient,
    )
    yield
    disconnect()


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
    session = SASession(bind=connection)

    yield session

    # Teardown
    #
    # Rollback everything that happened with the Session above (including
    # explicit commits).
    session.close()
    transaction.rollback()
    connection.close()
