"""Mork edx student models."""

import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKeyConstraint, Index, String
from sqlalchemy.dialects.mysql import INTEGER, TEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class StudentAnonymoususerid(Base):
    """Model for the `student_anonymoususerid` table."""

    __tablename__ = "student_anonymoususerid"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    user_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    anonymous_user_id: Mapped[str] = mapped_column(
        String(32), nullable=False, unique=True
    )
    course_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="student_anonymoususerid"
    )


class StudentCourseaccessrole(Base):
    """Model for the `student_courseaccessrole` table."""

    __tablename__ = "student_courseaccessrole"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
        ),
        Index(
            "student_courseaccessrole_user_id_3203176c4f474414_uniq",
            "user_id",
            "org",
            "course_id",
            "role",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    user_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    org: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    course_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="student_courseaccessrole"
    )


class StudentCourseenrollment(Base):
    """Model for the `student_courseenrollment` table."""

    __tablename__ = "student_courseenrollment"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
            name="user_id_refs_id_45948fcded37bc9d",
        ),
        Index("student_courseenrollment_3216ff68", "created"),
        Index("student_courseenrollment_fbfc09f1", "user_id"),
        Index("student_courseenrollment_ff48d8e5", "course_id"),
        Index(
            "student_courseenrollment_user_id_2d2a572f07dd8e37_uniq",
            "user_id",
            "course_id",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    user_id: Mapped[int] = mapped_column(INTEGER(11))
    course_id: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[int] = mapped_column(INTEGER(1))
    mode: Mapped[str] = mapped_column(String(100))
    created: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="student_courseenrollment"
    )

    student_courseenrollmentattribute: Mapped[
        List["StudentCourseenrollmentattribute"]
    ] = relationship(
        "StudentCourseenrollmentattribute",
        back_populates="enrollment",
        cascade="all, delete-orphan",
    )
    student_manualenrollmentaudit: Mapped[List["StudentManualenrollmentaudit"]] = (
        relationship(
            "StudentManualenrollmentaudit",
            back_populates="enrollment",
            cascade="all, delete-orphan",
        )
    )


class StudentCourseenrollmentallowed(Base):
    """Model for the `student_courseenrollmentallowed` table.

    At the database level, no foreign key is defined.
    """

    __tablename__ = "student_courseenrollmentallowed"
    __table_args__ = (
        Index(
            "student_courseenrollmentallowed_email_6f3eafd4a6c58591_uniq",
            "email",
            "course_id",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    course_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, index=True)
    auto_enroll: Mapped[int] = mapped_column(INTEGER(1), nullable=False)


class StudentCourseenrollmentattribute(Base):
    """Model for the `student_courseenrollmentattribute` table."""

    __tablename__ = "student_courseenrollmentattribute"
    __table_args__ = (
        ForeignKeyConstraint(
            ["enrollment_id"],
            ["student_courseenrollment.id"],
        ),
    )
    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    enrollment_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    namespace: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[str] = mapped_column(String(255), nullable=False)

    enrollment: Mapped["StudentCourseenrollment"] = relationship(
        "StudentCourseenrollment", back_populates="student_courseenrollmentattribute"
    )


class StudentHistoricalcourseenrollment(Base):
    """Model for the `student_historicalcourseenrollment` table."""

    __tablename__ = "student_historicalcourseenrollment"
    __table_args__ = (
        ForeignKeyConstraint(
            ["history_user_id"],
            ["auth_user.id"],
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    course_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, index=True)
    is_active: Mapped[int] = mapped_column(INTEGER(1), nullable=False)
    mode: Mapped[str] = mapped_column(String(100), nullable=False)
    user_id: Mapped[int] = mapped_column(INTEGER(11), index=True, nullable=True)
    history_id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    history_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    history_user_id: Mapped[int] = mapped_column(INTEGER(11), index=True, nullable=True)
    history_type: Mapped[str] = mapped_column(String(1), nullable=False)

    history_user = relationship(
        "AuthUser",
        foreign_keys=[history_user_id],
        primaryjoin="StudentHistoricalcourseenrollment.history_user_id == AuthUser.id",
        back_populates="student_historicalcourseenrollment_history_user",
    )
    user = relationship(
        "AuthUser",
        foreign_keys=[user_id, history_user_id],
        primaryjoin="StudentHistoricalcourseenrollment.user_id == AuthUser.id",
        back_populates="student_historicalcourseenrollment_user",
    )


class StudentLanguageproficiency(Base):
    """Model for the `student_languageproficiency` table."""

    __tablename__ = "student_languageproficiency"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_profile_id"],
            ["auth_userprofile.id"],
        ),
        Index(
            "student_languageproficiency_code_68e76171684c62e5_uniq",
            "code",
            "user_profile_id",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    user_profile_id: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, index=True
    )
    code: Mapped[str] = mapped_column(String(16), nullable=False)

    user_profile: Mapped["AuthUserprofile"] = relationship(  # noqa: F821
        "AuthUserprofile", back_populates="student_languageproficiency"
    )


class StudentLoginfailure(Base):
    """Model for the `student_loginfailures` table."""

    __tablename__ = "student_loginfailures"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    user_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    failure_count: Mapped[int] = mapped_column(INTEGER(11), nullable=False)
    lockout_until: Mapped[datetime.datetime] = mapped_column(DateTime)

    user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="student_loginfailures"
    )


class StudentManualenrollmentaudit(Base):
    """Model for the `student_manualenrollmentaudit` table."""

    __tablename__ = "student_manualenrollmentaudit"
    __table_args__ = (
        ForeignKeyConstraint(
            ["enrollment_id"],
            ["student_courseenrollment.id"],
        ),
        ForeignKeyConstraint(
            ["enrolled_by_id"],
            ["auth_user.id"],
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    enrollment_id: Mapped[int] = mapped_column(INTEGER(11), index=True)
    enrolled_by_id: Mapped[int] = mapped_column(INTEGER(11), index=True)
    enrolled_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    time_stamp: Mapped[datetime.datetime] = mapped_column(DateTime)
    state_transition: Mapped[str] = mapped_column(String(255), nullable=False)
    reason: Mapped[str] = mapped_column(TEXT)

    enrollment: Mapped["StudentCourseenrollment"] = relationship(
        "StudentCourseenrollment", back_populates="student_manualenrollmentaudit"
    )


class StudentPendingemailchange(Base):
    """Model for the `student_pendingemailchange` table."""

    __tablename__ = "student_pendingemailchange"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    user_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, unique=True)
    new_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    activation_key: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)

    user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="student_pendingemailchange"
    )


class StudentUserstanding(Base):
    """Model for the `student_userstanding` table."""

    __tablename__ = "student_userstanding"
    __table_args__ = (
        ForeignKeyConstraint(
            ["changed_by_id"],
            ["auth_user.id"],
        ),
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    user_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, unique=True)
    account_status: Mapped[str] = mapped_column(String(31), nullable=False)
    changed_by_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    standing_last_changed_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False
    )

    changed_by = relationship(
        "AuthUser",
        foreign_keys=[changed_by_id],
        primaryjoin="StudentUserstanding.changed_by_id == AuthUser.id",
        back_populates="student_userstanding_changed_by",
    )
    user = relationship(
        "AuthUser",
        foreign_keys=[user_id, changed_by_id],
        primaryjoin="StudentUserstanding.user_id == AuthUser.id",
        back_populates="student_userstanding_user",
    )
