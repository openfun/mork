"""Mork users models."""

import enum
from typing import List
from uuid import uuid4

from sqlalchemy import (
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mork.models import Base


class ServiceName(str, enum.Enum):
    """Enum for service names."""

    ASHLEY = "ashley"
    EDX = "edx"
    BREVO = "brevo"
    JOANIE = "joanie"


class DeletionReason(str, enum.Enum):
    """Enum for the reason of the deletion request."""

    USER_REQUESTED = "user_requested"
    GDPR = "gdpr"


class DeletionStatus(str, enum.Enum):
    """Enum for deletion statuses."""

    TO_DELETE = "to_delete"
    DELETING = "deleting"
    DELETED = "deleted"


class UserServiceStatus(Base):
    """Table for storing the user status for a service."""

    __tablename__ = "user_service_statuses"
    __table_args__ = (
        UniqueConstraint("user_id", "service_name", name="uq_record_service"),
        Index(
            "idx_user_service_status",
            "user_id",
            "service_name",
            "status",
        ),
        Index("idx_service_status", "service_name", "status"),
    )

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    service_name: Mapped[ServiceName] = mapped_column(
        Enum(ServiceName, name="service_name"), nullable=False
    )
    status: Mapped[DeletionStatus] = mapped_column(
        Enum(DeletionStatus, name="deletion_status"), nullable=False, default=False
    )

    user: Mapped["User"] = relationship("User", back_populates="service_statuses")


class User(Base):
    """Table for storing the users to delete."""

    __tablename__ = "users"

    filtered_attrs = []

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    username: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    edx_user_id: Mapped[int] = mapped_column(Integer(), unique=True)
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    reason: Mapped[DeletionReason] = mapped_column(
        Enum(DeletionReason, name="deletion_reason"), nullable=False
    )

    service_statuses: Mapped[List[UserServiceStatus]] = relationship(
        "UserServiceStatus",
        cascade="all, delete-orphan",
        back_populates="user",
    )
