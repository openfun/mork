"""Mork edx models."""

import datetime

from sqlalchemy import DateTime, ForeignKeyConstraint
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UtilRatelimitconfiguration(Base):
    """Model for the `util_ratelimitconfiguration` table."""

    __tablename__ = "util_ratelimitconfiguration"
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

    changed_by: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="util_ratelimitconfiguration"
    )
