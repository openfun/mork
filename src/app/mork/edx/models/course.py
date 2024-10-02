"""Mork edx course models."""

import datetime

from sqlalchemy import DateTime, ForeignKeyConstraint, Index, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class CourseActionStateCoursererunstate(Base):
    """Model for the `course_action_state_coursererunstate` table."""

    __tablename__ = "course_action_state_coursererunstate"
    __table_args__ = (
        ForeignKeyConstraint(
            ["created_user_id"],
            ["auth_user.id"],
            name="created_user_id_refs_id_1334640c1744bdeb",
        ),
        ForeignKeyConstraint(
            ["updated_user_id"],
            ["auth_user.id"],
            name="updated_user_id_refs_id_1334640c1744bdeb",
        ),
        Index(
            "course_action_state_coursererun_course_key_cf5da77ed3032d6_uniq",
            "course_key",
            "action",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    created_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    updated_time: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    created_user_id: Mapped[int] = mapped_column(INTEGER(11), index=True, nullable=True)
    updated_user_id: Mapped[int] = mapped_column(INTEGER(11), index=True, nullable=True)
    course_key: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(50), nullable=False)
    should_display: Mapped[int] = mapped_column(INTEGER(1), nullable=False)
    message: Mapped[str] = mapped_column(String(1000), nullable=False)
    source_course_key: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)

    created_user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser",
        foreign_keys=[created_user_id],
        back_populates="course_action_state_coursererunstate_created_user",
    )
    updated_user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser",
        foreign_keys=[updated_user_id],
        back_populates="course_action_state_coursererunstate_updated_user",
    )


class CourseCreatorsCoursecreator(Base):
    """Model for the `course_creators_coursecreator` table."""

    __tablename__ = "course_creators_coursecreator"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
        ),
    )
    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    user_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, unique=True)
    state_changed: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)
    state: Mapped[str] = mapped_column(String(24), nullable=False)
    note: Mapped[str] = mapped_column(String(512), nullable=False)

    user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="course_creators_coursecreator"
    )


class CourseGroupsCourseusergroupUsers(Base):
    """Model for the `course_groups_courseusergroup_users` table."""

    __tablename__ = "course_groups_courseusergroup_users"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
        ),
        Index("courseusergroup_id", "courseusergroup_id", "user_id", unique=True),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    courseusergroup_id: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)

    user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="course_groups_courseusergroup_users"
    )


class CourseGroupsCohortmembership(Base):
    """Model for the `course_groups_cohortmembership` table."""

    __tablename__ = "course_groups_cohortmembership"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
        ),
        Index(
            "course_groups_cohortmembership_user_id_395bddd0389ed7da_uniq",
            "user_id",
            "course_id",
            unique=True,
        ),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    course_user_group_id: Mapped[int] = mapped_column(
        INTEGER(11), nullable=False, index=True
    )
    user_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)
    course_id: Mapped[str] = mapped_column(String(255), nullable=False)

    user: Mapped["AuthUser"] = relationship(  # noqa: F821
        "AuthUser", back_populates="course_groups_cohortmembership"
    )
