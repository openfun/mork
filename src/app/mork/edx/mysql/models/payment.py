"""Mork edx payment models."""

import datetime as dt

from sqlalchemy import DateTime, ForeignKeyConstraint, Index
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class PaymentUseracceptance(Base):
    """Model for the `payment_useracceptance` table."""

    __tablename__ = "payment_useracceptance"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
        ),
        Index(
            "payment_useracceptance_user_id_743f016c85c1493e_uniq",
            "user_id",
            "terms_id",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    user_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    terms_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    datetime: Mapped[dt.datetime] = mapped_column(DateTime, nullable=False, index=True)

    user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="payment_useracceptance"
    )
