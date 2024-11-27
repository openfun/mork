"""Mork edx wiki models."""

import datetime

from sqlalchemy import DateTime, ForeignKeyConstraint, Index, String
from sqlalchemy.dialects.mysql import INTEGER, TEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class WikiArticle(Base):
    """Model for the `wiki_article` table."""

    __tablename__ = "wiki_article"
    __table_args__ = (
        ForeignKeyConstraint(
            ["owner_id"],
            ["auth_user.id"],
        ),
    )
    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    current_revision_id: Mapped[int] = mapped_column(INTEGER(11), unique=True)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    modified: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    owner_id: Mapped[int] = mapped_column(INTEGER(11), index=True)
    group_id: Mapped[int] = mapped_column(INTEGER(11), index=True)
    group_read: Mapped[int] = mapped_column(INTEGER(1), nullable=False)
    group_write: Mapped[int] = mapped_column(INTEGER(1), nullable=False)
    other_read: Mapped[int] = mapped_column(INTEGER(1), nullable=False)
    other_write: Mapped[int] = mapped_column(INTEGER(1), nullable=False)

    owner: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="wiki_article"
    )


class WikiArticlerevision(Base):
    """Model for the `wiki_articlerevision` table."""

    __tablename__ = "wiki_articlerevision"
    __table_args__ = (
        Index(
            "wiki_articlerevision_article_id_4b4e7910c8e7b2d0_uniq",
            "article_id",
            "revision_number",
            unique=True,
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    revision_number: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    user_message: Mapped[str] = mapped_column(TEXT, nullable=False)
    automatic_log: Mapped[str] = mapped_column(TEXT, nullable=False)
    ip_address: Mapped[str] = mapped_column(String(15))
    user_id: Mapped[int] = mapped_column(INTEGER(11), index=True)
    modified: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    previous_revision_id: Mapped[int] = mapped_column(INTEGER(11), index=True)
    deleted: Mapped[int] = mapped_column(INTEGER(1), nullable=False)
    locked: Mapped[int] = mapped_column(INTEGER(1), nullable=False)
    article_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    content: Mapped[str] = mapped_column(TEXT, nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)

    user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="wiki_articlerevision"
    )
