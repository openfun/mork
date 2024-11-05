"""Mork models."""

from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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

    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
