"""Mork edx django models."""

from sqlalchemy import ForeignKeyConstraint, Index
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class DjangoCommentClientRoleUsers(Base):
    """Model for the `django_comment_client_role_users` table."""

    __tablename__ = "django_comment_client_role_users"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
        ),
        Index(
            "django_comment_client_role_users_role_id_78e483f531943614_uniq",
            "role_id",
            "user_id",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    role_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)

    user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="django_comment_client_role_users"
    )
