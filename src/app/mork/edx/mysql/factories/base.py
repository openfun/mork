"""Factory base configuration."""

import factory
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from mork.edx.mysql.models.base import Base

faker = Faker()
engine = create_engine("sqlite+pysqlite:///:memory:", echo=False, pool_pre_ping=True)
Base.metadata.create_all(engine)

Session = scoped_session(sessionmaker())


class BaseSQLAlchemyModelFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Base factory class for SQLAlchemy models."""

    class Meta:
        """Factory configuration."""

        abstract = True
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = None
