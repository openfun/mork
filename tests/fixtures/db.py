"""Edx database test fixtures."""

import pytest

from mork.edx.database import OpenEdxDB
from mork.edx.factories import engine, session
from mork.edx.models import Base


@pytest.fixture
def edx_db():
    """"""
    db = OpenEdxDB(engine, session)
    Base.metadata.create_all(engine)
    yield db
    db.session.rollback()
