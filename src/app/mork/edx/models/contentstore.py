"""Mork edx models."""

import datetime

from sqlalchemy import DateTime, ForeignKeyConstraint
from sqlalchemy.dialects.mysql import INTEGER, TEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class ContentstoreVideouploadconfig(Base):
    """Model for the `contentstore_videouploadconfig` table."""

    __tablename__ = "contentstore_videouploadconfig"
    __table_args__ = (
        ForeignKeyConstraint(
            ["changed_by_id"],
            ["auth_user.id"],
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    change_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    changed_by_id: Mapped[int] = mapped_column(INTEGER(11), index=True)
    enabled: Mapped[int] = mapped_column(INTEGER(1), nullable=False)
    profile_whitelist: Mapped[str] = mapped_column(TEXT, nullable=False)

    changed_by: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="contentstore_videouploadconfig"
    )
