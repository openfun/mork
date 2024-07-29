"""Factory classes for generating fake data for testing."""

import factory
from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, registry

from mork.edx import models

faker = Faker()
engine = create_engine("sqlite+pysqlite:///:memory:", echo=False, pool_pre_ping=True)
session = Session(engine)
registry().metadata.create_all(engine)


class EdxUserFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Factory for generating fake Open edX users."""

    class Meta:
        """Factory configuration."""

        model = models.User
        sqlalchemy_session = session

    id = factory.Sequence(lambda n: n)
    username = factory.Sequence(lambda n: f"{faker.user_name()}{n}")
    email = factory.Faker("email")
    is_staff = False
    is_superuser = False
    last_login = factory.Faker("date_time")
