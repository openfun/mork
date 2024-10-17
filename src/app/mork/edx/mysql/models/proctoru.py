"""Mork edx proctoru models."""

import datetime

from sqlalchemy import DateTime, ForeignKeyConstraint, Index, String
from sqlalchemy.dialects.mysql import INTEGER, TEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ProctoruProctoruexam(Base):
    """Model for the `proctoru_proctoruexam` table."""

    __tablename__ = "proctoru_proctoruexam"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
        ),
        Index(
            "proctoru_proctoruexam_user_id_2d5ce6ea053f2d80_uniq",
            "user_id",
            "block_id",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    user_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    start_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    actual_start_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    is_completed: Mapped[int] = mapped_column(INTEGER(1), nullable=False)
    is_started: Mapped[int] = mapped_column(INTEGER(1), nullable=False)
    is_canceled: Mapped[int] = mapped_column(INTEGER(1), nullable=False)
    block_id: Mapped[str] = mapped_column(String(200), nullable=False)
    end_time: Mapped[datetime.datetime] = mapped_column(DateTime)
    reservation_id: Mapped[str] = mapped_column(String(50), nullable=False)
    reservation_no: Mapped[str] = mapped_column(String(200), nullable=False)
    url: Mapped[str] = mapped_column(TEXT, nullable=False)

    user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="proctoru_proctoruexam"
    )


class ProctoruProctoruuser(Base):
    """Model for the `proctoru_proctoruuser` table."""

    __tablename__ = "proctoru_proctoruuser"
    __table_args__ = (
        ForeignKeyConstraint(
            ["student_id"],
            ["auth_user.id"],
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    student_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, unique=True)
    phone_number: Mapped[str] = mapped_column(String(100), nullable=False)
    time_zone: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str] = mapped_column(TEXT, nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False)
    date_created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    time_zone_display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False)

    student: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="proctoru_proctoruuser"
    )
