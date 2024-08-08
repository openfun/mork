"""Mork models."""

import datetime
import uuid

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID
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


class EmailStatus(Base):
    """Model for storing email statuses."""

    __tablename__ = "email_status"

    filtered_attrs = ["email"]

    id: Mapped[int] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(254), unique=True)
    sent_date: Mapped[datetime.datetime] = mapped_column(DateTime)
