"""Mork edx models."""

import datetime
from typing import Optional

from sqlalchemy import DateTime, Index, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from mork.edx.mixins import UserMixin


class Base(DeclarativeBase):
    """Base class for all models in the database."""

    filtered_attrs = []

    def safe_dict(self):
        """Return a dictionary representation of the model."""
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if c.name not in self.filtered_attrs
        }


class User(UserMixin, Base):
    """Model for the `auth_user` table."""

    __tablename__ = "auth_user"
    __table_args__table_args__ = (
        Index("email", "email", unique=True),
        Index("username", "username", unique=True),
    )
    filtered_attrs = ["username", "email"]

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    username: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(254))
    is_staff: Mapped[int] = mapped_column(INTEGER(1))
    is_superuser: Mapped[int] = mapped_column(INTEGER(1))
    last_login: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
