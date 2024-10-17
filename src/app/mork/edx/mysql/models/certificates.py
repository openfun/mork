"""Mork edx certificates models."""

import datetime

from sqlalchemy import DateTime, ForeignKeyConstraint, Index, String
from sqlalchemy.dialects.mysql import INTEGER, TEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class CertificatesCertificatehtmlviewconfiguration(Base):
    """Model for the `certificates_certificatehtmlviewconfiguration` table."""

    __tablename__ = "certificates_certificatehtmlviewconfiguration"
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
    configuration: Mapped[str] = mapped_column(TEXT, nullable=False)

    changed_by: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="certificates_certificatehtmlviewconfiguration"
    )


class CertificatesGeneratedcertificate(Base):
    """Model for the `certificates_generatedcertificate` table."""

    __tablename__ = "certificates_generatedcertificate"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
            name="user_id_refs_id_6c4fb3478e23bfe2",
        ),
        Index(
            "certificates_generatedcertific_verify_uuid_1b5a14bb83c471ff_uniq",
            "verify_uuid",
        ),
        Index(
            "certificates_generatedcertifica_course_id_1389f6b2d72f5e78_uniq",
            "course_id",
            "user_id",
            unique=True,
        ),
        Index("certificates_generatedcertificate_fbfc09f1", "user_id"),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    user_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    download_url: Mapped[str] = mapped_column(String(128), nullable=False)
    grade: Mapped[str] = mapped_column(String(5), nullable=False)
    course_id: Mapped[str] = mapped_column(String(255), nullable=False)
    key: Mapped[str] = mapped_column(String(32), nullable=False)
    distinction: Mapped[int] = mapped_column(INTEGER(1), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    verify_uuid: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    download_uuid: Mapped[str] = mapped_column(String(32), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    modified_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    error_reason: Mapped[str] = mapped_column(String(512), nullable=False)
    mode: Mapped[str] = mapped_column(String(32), nullable=False)

    user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="certificates_generatedcertificate"
    )
