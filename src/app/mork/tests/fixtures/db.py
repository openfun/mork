"""Edx database test fixtures."""

import mongomock
import pytest
from alembic import command
from alembic.config import Config
from mongoengine import connect, disconnect
from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SASession

from mork.api.v1 import app as v1
from mork.conf import settings
from mork.db import get_session
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

    # Pretend to have all migrations applied
    alembic_cfg = Config(settings.ALEMBIC_CFG_PATH)
    alembic_cfg.set_main_option("sqlalchemy.url", settings.TEST_DB_URL)
    command.stamp(alembic_cfg, "head")

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


@pytest.fixture(autouse=True)
def override_db_test_session(db_session):
    """Use test database along with a test session by default."""

    def get_session_override():
        return db_session

    v1.dependency_overrides[get_session] = get_session_override

    yield
