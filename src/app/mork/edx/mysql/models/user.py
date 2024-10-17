"""Mork edx user models."""

from sqlalchemy import ForeignKeyConstraint, Index, String
from sqlalchemy.dialects.mysql import INTEGER, TEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class UserApiUserpreference(Base):
    """Model for the `user_api_userpreference` table."""

    __tablename__ = "user_api_userpreference"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
            name="user_id_refs_id_2839c1f4f3473b9e",
        ),
        Index("user_api_userpreference_45544485", "key"),
        Index("user_api_userpreference_fbfc09f1", "user_id"),
        Index(
            "user_api_userpreference_user_id_4e4942d73f760072_uniq",
            "user_id",
            "key",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    user_id: Mapped[int] = mapped_column(INTEGER(11))
    key: Mapped[str] = mapped_column(String(255))
    value: Mapped[str] = mapped_column(TEXT)

    user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="user_api_userpreference"
    )
