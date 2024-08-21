"""Seed the edx database with test data."""

import asyncio

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mork.conf import settings
from mork.edx.factories.auth import EdxAuthUserFactory
from mork.edx.models.base import Base


async def seed_edx_database():
    """Seed the MySQL edx database with mocked data."""
    engine = create_engine(settings.EDX_DB_URL)
    session = Session(engine)
    EdxAuthUserFactory._meta.sqlalchemy_session = session  # noqa: SLF001
    EdxAuthUserFactory._meta.sqlalchemy_session_persistence = "commit"  # noqa: SLF001
    Base.metadata.create_all(engine)

    EdxAuthUserFactory.create_batch(1000)


if __name__ == "__main__":
    asyncio.run(seed_edx_database())
