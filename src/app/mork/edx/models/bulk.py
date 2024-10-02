"""Mork edx bulk models."""

import datetime

from sqlalchemy import DateTime, ForeignKeyConstraint, Index, String
from sqlalchemy.dialects.mysql import INTEGER, TEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class BulkEmailCourseemail(Base):
    """Model for the `bulk_email_courseemail` table."""

    __tablename__ = "bulk_email_courseemail"
    __table_args__ = (
        ForeignKeyConstraint(
            ["sender_id"],
            ["auth_user.id"],
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    sender_id: Mapped[int] = mapped_column(INTEGER(11))
    slug: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(128), nullable=False)
    html_message: Mapped[str] = mapped_column(TEXT)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    modified: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    course_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    to_option: Mapped[str] = mapped_column(String(64), nullable=False)
    text_message: Mapped[str] = mapped_column(TEXT)
    template_name: Mapped[str] = mapped_column(String(255))
    from_addr: Mapped[str] = mapped_column(String(255))

    sender: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="bulk_email_courseemail"
    )


class BulkEmailOptout(Base):
    """Model for the `bulk_email_optout` table."""

    __tablename__ = "bulk_email_optout"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
        ),
        Index(
            "bulk_email_optout_course_id_368f7519b2997e1a_uniq",
            "course_id",
            "user_id",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    course_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(INTEGER(11), index=True)

    user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="bulk_email_optout"
    )
