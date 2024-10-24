"""Mork edx instructor models."""

import datetime

from sqlalchemy import DateTime, ForeignKeyConstraint, String
from sqlalchemy.dialects.mysql import INTEGER, TEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class InstructorTaskInstructortask(Base):
    """Model for the `instructor_task_instructortask` table."""

    __tablename__ = "instructor_task_instructortask"
    __table_args__ = (
        ForeignKeyConstraint(
            ["requester_id"],
            ["auth_user.id"],
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    course_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    task_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    task_input: Mapped[str] = mapped_column(String(255), nullable=False)
    task_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    task_state: Mapped[str] = mapped_column(String(50), index=True)
    task_output: Mapped[str] = mapped_column(String(1024))
    requester_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    created: Mapped[datetime.datetime] = mapped_column(DateTime)
    updated: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    subtasks: Mapped[str] = mapped_column(TEXT, nullable=False)

    requester: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="instructor_task_instructortask"
    )
