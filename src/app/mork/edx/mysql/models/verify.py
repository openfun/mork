"""Mork edx verify models."""

import datetime

from sqlalchemy import DateTime, ForeignKeyConstraint, String
from sqlalchemy.dialects.mysql import INTEGER, TEXT
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


class VerifyStudentSoftwaresecurephotoverification(Base):
    """Model for the `verify_student_softwaresecurephotoverification` table."""

    __tablename__ = "verify_student_softwaresecurephotoverification"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
        ),
        ForeignKeyConstraint(
            ["reviewing_user_id"],
            ["auth_user.id"],
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    status: Mapped[str] = mapped_column(String(100), nullable=False)
    status_changed: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    user_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    face_image_url: Mapped[str] = mapped_column(String(255), nullable=False)
    photo_id_image_url: Mapped[str] = mapped_column(String(255), nullable=False)
    receipt_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )
    submitted_at: Mapped[datetime.datetime] = mapped_column(DateTime, index=True)
    reviewing_user_id: Mapped[int] = mapped_column(INTEGER(11), index=True)
    reviewing_service: Mapped[str] = mapped_column(String(255), nullable=False)
    error_msg: Mapped[str] = mapped_column(TEXT, nullable=False)
    error_code: Mapped[str] = mapped_column(String(50), nullable=False)
    photo_id_key: Mapped[str] = mapped_column(TEXT, nullable=False)
    display: Mapped[int] = mapped_column(INTEGER(1), nullable=False, index=True)
    copy_id_photo_from_id: Mapped[int] = mapped_column(INTEGER(11), index=True)

    reviewing_user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser",
        primaryjoin="VerifyStudentSoftwaresecurephotoverification.reviewing_user_id == AuthUser.id",  # noqa: E501
        back_populates="verify_student_softwaresecurephotoverification_reviewing_user",
    )
    user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser",
        primaryjoin="VerifyStudentSoftwaresecurephotoverification.user_id == AuthUser.id",  # noqa: E501
        back_populates="verify_student_softwaresecurephotoverification_user",
    )
