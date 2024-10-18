"""Seed the edx database with test data."""

import asyncio

from sqlalchemy import create_engine

from mongoengine import connect, disconnect

from mork.edx.mongo.factories import CommentFactory, CommentThreadFactory
from mork.conf import settings
from mork.edx.mysql.factories.auth import EdxAuthUserFactory
from mork.edx.mysql.factories.base import BaseSQLAlchemyModelFactory, Session
from mork.edx.mysql.models.base import Base


async def seed_edx_mysql_database():
    """Seed the MySQL edx database with mocked data."""
    engine = create_engine(settings.EDX_MYSQL_DB_URL)
    Session.configure(bind=engine)
    BaseSQLAlchemyModelFactory._meta.sqlalchemy_session = Session  # noqa: SLF001
    Base.metadata.create_all(engine)

    EdxAuthUserFactory.create_batch(100)
    Session.commit()


async def seed_edx_mongodb_database():
    """Seed the MongoDB edx database with mocked data."""
    connect(host=settings.EDX_MONGO_DB_HOST, db=settings.EDX_MONGO_DB_NAME)

    CommentFactory.create_batch(1000)
    CommentThreadFactory.create_batch(1000)

    disconnect(alias="mongodb")


async def main():
    tasks = [seed_edx_mysql_database(), seed_edx_mongodb_database()]
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
