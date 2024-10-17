"""Mork edx courseware models."""

import datetime
from typing import List

from sqlalchemy import DateTime, Float, ForeignKeyConstraint, Index, String
from sqlalchemy.dialects.mysql import INTEGER, TEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class CoursewareOfflinecomputedgrade(Base):
    """Model for the `courseware_offlinecomputedgrade` table."""

    __tablename__ = "courseware_offlinecomputedgrade"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
        ),
        Index(
            "courseware_offlinecomputedgrade_user_id_46133bbd0926078f_uniq",
            "user_id",
            "course_id",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    user_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    course_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created: Mapped[datetime.datetime] = mapped_column(DateTime, index=True)
    updated: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )
    gradeset: Mapped[str] = mapped_column(TEXT)

    user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="courseware_offlinecomputedgrade"
    )


class CoursewareStudentmodule(Base):
    """Model for the `courseware_studentmodule` table."""

    __tablename__ = "courseware_studentmodule"
    __table_args__ = (
        ForeignKeyConstraint(
            ["student_id"],
            ["auth_user.id"],
            name="student_id_refs_id_51af713179ba2570",
        ),
        Index(
            "courseware_studentmodule_student_id_635d77aea1256de5_uniq",
            "student_id",
            "module_id",
            "course_id",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    module_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    module_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    student_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    state: Mapped[str] = mapped_column(TEXT)
    grade: Mapped[float] = mapped_column(Float(asdecimal=True), index=True)
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )
    modified: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )
    max_grade: Mapped[float] = mapped_column(Float(asdecimal=True))
    done: Mapped[str] = mapped_column(String(8), nullable=False, index=True)
    course_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)

    student: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="courseware_studentmodule"
    )

    courseware_studentmodulehistory: Mapped[List["CoursewareStudentmodulehistory"]] = (
        relationship(
            "CoursewareStudentmodulehistory",
            back_populates="student_module",
            cascade="all, delete-orphan",
        )
    )


class CoursewareStudentmodulehistory(Base):
    """Model for the `courseware_studentmodulehistory` table."""

    __tablename__ = "courseware_studentmodulehistory"
    __table_args__ = (
        ForeignKeyConstraint(
            ["student_module_id"],
            ["courseware_studentmodule.id"],
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    student_module_id: Mapped["CoursewareStudentmodule"] = mapped_column(
        INTEGER(11), nullable=False, index=True
    )
    version: Mapped[str] = mapped_column(String(255), index=True)
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )
    state: Mapped[str] = mapped_column(TEXT)
    grade: Mapped[float] = mapped_column(Float(asdecimal=True))
    max_grade: Mapped[float] = mapped_column(Float(asdecimal=True))

    student_module: Mapped["CoursewareStudentmodule"] = relationship(
        "CoursewareStudentmodule", back_populates="courseware_studentmodulehistory"
    )


class CoursewareXmodulestudentinfofield(Base):
    """Model for the `courseware_xmodulestudentinfofield` table."""

    __tablename__ = "courseware_xmodulestudentinfofield"
    __table_args__ = (
        ForeignKeyConstraint(
            ["student_id"],
            ["auth_user.id"],
        ),
        Index(
            "courseware_xmodulestudentinfof_student_id_33f2f772c49db067_uniq",
            "student_id",
            "field_name",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    field_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    value: Mapped[str] = mapped_column(TEXT, nullable=False)
    student_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )
    modified: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )

    student: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="courseware_xmodulestudentinfofield"
    )


class CoursewareXmodulestudentprefsfield(Base):
    """Model for the `courseware_xmodulestudentprefsfield` table."""

    __tablename__ = "courseware_xmodulestudentprefsfield"
    __table_args__ = (
        ForeignKeyConstraint(
            ["student_id"],
            ["auth_user.id"],
        ),
        Index(
            "courseware_xmodulestudentprefs_student_id_2a5d275498b7a407_uniq",
            "student_id",
            "module_type",
            "field_name",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    field_name: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    module_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    value: Mapped[str] = mapped_column(TEXT, nullable=False)
    student_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    created: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )
    modified: Mapped[datetime.datetime] = mapped_column(
        DateTime, nullable=False, index=True
    )

    student: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="courseware_xmodulestudentprefsfield"
    )
