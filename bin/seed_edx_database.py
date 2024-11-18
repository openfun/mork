"""Seed the edx database with test data."""

from sqlalchemy import create_engine

from mongoengine import connect, disconnect

from mork.edx.mongo.factories import CommentFactory, CommentThreadFactory
from mork.conf import settings
from mork.edx.mysql.factories.auth import EdxAuthUserFactory
from mork.edx.mysql.factories.base import BaseSQLAlchemyModelFactory, Session
from mork.edx.mysql.models.base import Base


def seed_edx_mysql_database(batch_size: int = 100):
    """Seed the MySQL edx database with mocked data."""
    engine = create_engine(settings.EDX_MYSQL_DB_URL)
    Session.configure(bind=engine)
    BaseSQLAlchemyModelFactory._meta.sqlalchemy_session = Session  # noqa: SLF001
    Base.metadata.create_all(engine)

    users = EdxAuthUserFactory.create_batch(batch_size)
    usernames = [user.username for user in users]

    Session.commit()
    return usernames


def seed_edx_mongodb_database(batch_size: int = 1000, usernames: list[str] = []):
    """Seed the MongoDB edx database with mocked data using existing usernames."""
    connect(host=settings.EDX_MONGO_DB_URL)

    CommentFactory.create_batch(batch_size, usernames=usernames)
    CommentThreadFactory.create_batch(batch_size, usernames=usernames)

    disconnect()


if __name__ == "__main__":
    usernames = seed_edx_mysql_database()
    seed_edx_mongodb_database(usernames=usernames)
