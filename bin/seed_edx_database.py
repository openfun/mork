"""Seed the edx database with test data."""

import asyncio

from sqlalchemy import create_engine

from mork.conf import settings
from mork.edx.factories.auth import EdxAuthUserFactory
from mork.edx.factories.base import BaseSQLAlchemyModelFactory, Session
from mork.edx.models.base import Base


async def seed_edx_database():
    """Seed the MySQL edx database with mocked data."""
    engine = create_engine(settings.EDX_DB_URL)
    Session.configure(bind=engine)
    BaseSQLAlchemyModelFactory._meta.sqlalchemy_session = Session  # noqa: SLF001
    Base.metadata.create_all(engine)

    EdxAuthUserFactory.create_batch(100)
    Session.commit()


if __name__ == "__main__":
    asyncio.run(seed_edx_database())
