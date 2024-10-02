"""Mork edx notify models."""

from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class NotifySetting(Base):
    """Model for the `notify_settings` table."""

    __tablename__ = "notify_settings"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    user_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    interval: Mapped[int] = mapped_column(INTEGER(6), nullable=False)

    user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="notify_settings"
    )
