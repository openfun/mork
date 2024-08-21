"""Factory base configuration."""

from faker import Faker
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from mork.edx.models.base import Base

faker = Faker()
engine = create_engine("sqlite+pysqlite:///:memory:", echo=False, pool_pre_ping=True)
session = Session(engine)
Base.metadata.create_all(engine)
