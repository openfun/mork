"""Mork tasks models."""

import datetime
import uuid

from sqlalchemy import DateTime, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from mork.models import Base


class EmailStatus(Base):
    """Model for storing email statuses."""

    __tablename__ = "email_status"

    filtered_attrs = ["email"]

    id: Mapped[int] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(254), unique=True)
    sent_date: Mapped[datetime.datetime] = mapped_column(DateTime)
