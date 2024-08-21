"""Mork edx models."""

import datetime

from sqlalchemy import DateTime, ForeignKeyConstraint, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class VerifyStudentHistoricalverificationdeadline(Base):
    """Model for the `verify_student_historicalverificationdeadline` table."""

    __tablename__ = "verify_student_historicalverificationdeadline"
    __table_args__ = (
        ForeignKeyConstraint(
            ["history_user_id"],
            ["auth_user.id"],
        ),
    )
    id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    modified: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    course_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    deadline: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    history_id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    history_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    history_user_id: Mapped[int] = mapped_column(INTEGER(11), index=True)
    history_type: Mapped[str] = mapped_column(String(1), nullable=False)
    deadline_is_explicit: Mapped[int] = mapped_column(INTEGER(1), nullable=False)

    history_user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="verify_student_historicalverificationdeadline"
    )
