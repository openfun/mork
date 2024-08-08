"""Seed the edx database with test data."""

import asyncio

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mork.conf import settings
from mork.edx.factories import EdxUserFactory
from mork.edx.models import Base


async def seed_edx_database():
    """Seed the MySQL edx database with mocked data."""
    engine = create_engine(settings.EDX_DB_URL)
    session = Session(engine)
    EdxUserFactory._meta.sqlalchemy_session = session  # noqa: SLF001
    EdxUserFactory._meta.sqlalchemy_session_persistence = "commit"  # noqa: SLF001
    Base.metadata.create_all(engine)

    EdxUserFactory.create_batch(1000)


if __name__ == "__main__":
    asyncio.run(seed_edx_database())
