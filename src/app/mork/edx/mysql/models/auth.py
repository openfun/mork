"""Mork edx auth models."""

import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKeyConstraint, Index, String
from sqlalchemy.dialects.mysql import INTEGER, TEXT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .bulk import BulkEmailCourseemail, BulkEmailOptout
from .certificates import (
    CertificatesCertificatehtmlviewconfiguration,
    CertificatesGeneratedcertificate,
)
from .contentstore import ContentstoreVideouploadconfig
from .course import (
    CourseActionStateCoursererunstate,
    CourseCreatorsCoursecreator,
    CourseGroupsCohortmembership,
    CourseGroupsCourseusergroupUsers,
)
from .courseware import (
    CoursewareOfflinecomputedgrade,
    CoursewareStudentmodule,
    CoursewareXmodulestudentinfofield,
    CoursewareXmodulestudentprefsfield,
)
from .dark import DarkLangDarklangconfig
from .django import DjangoCommentClientRoleUsers
from .instructor import InstructorTaskInstructortask
from .notify import NotifySetting
from .payment import PaymentUseracceptance
from .proctoru import ProctoruProctoruexam, ProctoruProctoruuser
from .student import (
    StudentAnonymoususerid,
    StudentCourseaccessrole,
    StudentCourseenrollment,
    StudentHistoricalcourseenrollment,
    StudentLanguageproficiency,
    StudentLoginfailure,
    StudentPendingemailchange,
    StudentUserstanding,
)
from .user import UserApiUserpreference
from .util import UtilRatelimitconfiguration
from .verify import (
    VerifyStudentHistoricalverificationdeadline,
    VerifyStudentSoftwaresecurephotoverification,
)


class AuthUser(Base):
    """Model for the `auth_user` table."""

    __tablename__ = "auth_user"
    __table_args__ = (
        Index("email", "email", unique=True),
        Index("username", "username", unique=True),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    username: Mapped[str] = mapped_column(String(30))
    first_name: Mapped[str] = mapped_column(String(30))
    last_name: Mapped[str] = mapped_column(String(30))
    email: Mapped[str] = mapped_column(String(254))
    password: Mapped[str] = mapped_column(String(128))
    is_staff: Mapped[int] = mapped_column(INTEGER(1))
    is_active: Mapped[int] = mapped_column(INTEGER(1))
    is_superuser: Mapped[int] = mapped_column(INTEGER(1))
    date_joined: Mapped[datetime.datetime] = mapped_column(DateTime)
    last_login: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    auth_registration: Mapped["AuthRegistration"] = relationship(
        "AuthRegistration",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    authtoken_token: Mapped["AuthtokenToken"] = relationship(
        "AuthtokenToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    auth_userprofile: Mapped["AuthUserprofile"] = relationship(
        "AuthUserprofile",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    auth_user_groups: Mapped["AuthUserGroups"] = relationship(
        "AuthUserGroups",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    bulk_email_courseemail: Mapped[List["BulkEmailCourseemail"]] = relationship(
        "BulkEmailCourseemail",
        back_populates="sender",
        cascade="all, delete-orphan",
    )
    bulk_email_optout: Mapped[List["BulkEmailOptout"]] = relationship(
        "BulkEmailOptout",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    certificates_certificatehtmlviewconfiguration: Mapped[
        List["CertificatesCertificatehtmlviewconfiguration"]
    ] = relationship(
        "CertificatesCertificatehtmlviewconfiguration",
        back_populates="changed_by",
        cascade="all, delete-orphan",
    )
    certificates_generatedcertificate: Mapped[
        List["CertificatesGeneratedcertificate"]
    ] = relationship(
        "CertificatesGeneratedcertificate",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    contentstore_videouploadconfig: Mapped[List["ContentstoreVideouploadconfig"]] = (
        relationship(
            "ContentstoreVideouploadconfig",
            back_populates="changed_by",
            cascade="all, delete-orphan",
        )
    )
    course_action_state_coursererunstate_created_user: Mapped[
        List["CourseActionStateCoursererunstate"]
    ] = relationship(
        "CourseActionStateCoursererunstate",
        back_populates="created_user",
        cascade="all, delete-orphan",
        foreign_keys=[CourseActionStateCoursererunstate.created_user_id],
    )
    course_action_state_coursererunstate_updated_user: Mapped[
        List["CourseActionStateCoursererunstate"]
    ] = relationship(
        "CourseActionStateCoursererunstate",
        back_populates="updated_user",
        cascade="all, delete-orphan",
        foreign_keys=[CourseActionStateCoursererunstate.updated_user_id],
    )
    course_groups_courseusergroup_users: Mapped[
        List["CourseGroupsCourseusergroupUsers"]
    ] = relationship(
        "CourseGroupsCourseusergroupUsers",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    course_groups_cohortmembership: Mapped[List["CourseGroupsCohortmembership"]] = (
        relationship(
            "CourseGroupsCohortmembership",
            back_populates="user",
            cascade="all, delete-orphan",
        )
    )
    course_creators_coursecreator: Mapped["CourseCreatorsCoursecreator"] = relationship(
        "CourseCreatorsCoursecreator",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    courseware_offlinecomputedgrade: Mapped[List["CoursewareOfflinecomputedgrade"]] = (
        relationship(
            "CoursewareOfflinecomputedgrade",
            back_populates="user",
            cascade="all, delete-orphan",
        )
    )
    courseware_studentmodule: Mapped[List["CoursewareStudentmodule"]] = relationship(
        "CoursewareStudentmodule",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    courseware_xmodulestudentinfofield: Mapped[
        List["CoursewareXmodulestudentinfofield"]
    ] = relationship(
        "CoursewareXmodulestudentinfofield",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    courseware_xmodulestudentprefsfield: Mapped[
        List["CoursewareXmodulestudentprefsfield"]
    ] = relationship(
        "CoursewareXmodulestudentprefsfield",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    django_comment_client_role_users: Mapped[List["DjangoCommentClientRoleUsers"]] = (
        relationship(
            "DjangoCommentClientRoleUsers",
            back_populates="user",
            cascade="all, delete-orphan",
        )
    )
    dark_lang_darklangconfig: Mapped[List["DarkLangDarklangconfig"]] = relationship(
        "DarkLangDarklangconfig",
        back_populates="changed_by",
        cascade="all, delete-orphan",
    )
    instructor_task_instructortask: Mapped[List["InstructorTaskInstructortask"]] = (
        relationship(
            "InstructorTaskInstructortask",
            back_populates="requester",
            cascade="all, delete-orphan",
        )
    )
    notify_settings: Mapped[List["NotifySetting"]] = relationship(
        "NotifySetting",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    payment_useracceptance: Mapped[List["PaymentUseracceptance"]] = relationship(
        "PaymentUseracceptance",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    proctoru_proctoruexam: Mapped[List["ProctoruProctoruexam"]] = relationship(
        "ProctoruProctoruexam",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    proctoru_proctoruuser: Mapped["ProctoruProctoruuser"] = relationship(
        "ProctoruProctoruuser",
        back_populates="student",
        cascade="all, delete-orphan",
    )
    student_anonymoususerid: Mapped[List["StudentAnonymoususerid"]] = relationship(
        "StudentAnonymoususerid",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    student_courseaccessrole: Mapped[List["StudentCourseaccessrole"]] = relationship(
        "StudentCourseaccessrole",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    student_courseenrollment: Mapped[List["StudentCourseenrollment"]] = relationship(
        "StudentCourseenrollment",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    student_historicalcourseenrollment_history_user: Mapped[
        List["StudentHistoricalcourseenrollment"]
    ] = relationship(
        "StudentHistoricalcourseenrollment",
        foreign_keys=[StudentHistoricalcourseenrollment.history_user_id],
        back_populates="history_user",
        cascade="all, delete-orphan",
    )
    student_historicalcourseenrollment_user: Mapped[
        List["StudentHistoricalcourseenrollment"]
    ] = relationship(
        "StudentHistoricalcourseenrollment",
        foreign_keys=[StudentHistoricalcourseenrollment.user_id],
        back_populates="user",
        cascade="all, delete-orphan",
    )
    student_loginfailures: Mapped[List["StudentLoginfailure"]] = relationship(
        "StudentLoginfailure",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    student_pendingemailchange: Mapped["StudentPendingemailchange"] = relationship(
        "StudentPendingemailchange",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    student_userstanding_changed_by: Mapped["StudentUserstanding"] = relationship(
        "StudentUserstanding",
        foreign_keys=[StudentUserstanding.changed_by_id],
        primaryjoin="StudentUserstanding.changed_by_id == AuthUser.id",
        back_populates="changed_by",
        cascade="all, delete-orphan",
    )
    student_userstanding_user: Mapped["StudentUserstanding"] = relationship(
        "StudentUserstanding",
        foreign_keys=[StudentUserstanding.user_id, StudentUserstanding.changed_by_id],
        primaryjoin="StudentUserstanding.user_id == AuthUser.id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    user_api_userpreference: Mapped[List["UserApiUserpreference"]] = relationship(
        "UserApiUserpreference",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    util_ratelimitconfiguration: Mapped[List["UtilRatelimitconfiguration"]] = (
        relationship(
            "UtilRatelimitconfiguration",
            back_populates="changed_by",
            cascade="all, delete-orphan",
        )
    )
    verify_student_historicalverificationdeadline: Mapped[
        List["VerifyStudentHistoricalverificationdeadline"]
    ] = relationship(
        "VerifyStudentHistoricalverificationdeadline",
        back_populates="history_user",
        cascade="all, delete-orphan",
    )
    verify_student_softwaresecurephotoverification_reviewing_user: Mapped[
        List["VerifyStudentSoftwaresecurephotoverification"]
    ] = relationship(
        "VerifyStudentSoftwaresecurephotoverification",
        foreign_keys=[VerifyStudentSoftwaresecurephotoverification.reviewing_user_id],
        primaryjoin="VerifyStudentSoftwaresecurephotoverification.reviewing_user_id == AuthUser.id",  # noqa: E501
        back_populates="reviewing_user",
        cascade="all, delete-orphan",
    )
    verify_student_softwaresecurephotoverification_user: Mapped[
        List["VerifyStudentSoftwaresecurephotoverification"]
    ] = relationship(
        "VerifyStudentSoftwaresecurephotoverification",
        foreign_keys=[VerifyStudentSoftwaresecurephotoverification.user_id],
        primaryjoin="VerifyStudentSoftwaresecurephotoverification.user_id == AuthUser.id",  # noqa: E501
        back_populates="user",
        cascade="all, delete-orphan",
    )


class AuthUserGroups(Base):
    """Model for the `auth_user_groups`table."""

    __tablename__ = "auth_user_groups"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
        ),
        Index("user_id_auth_user_groups", "user_id", "group_id", unique=True),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    user_id: Mapped["AuthUser"] = mapped_column(INTEGER(11), nullable=False, index=True)
    group_id: Mapped[int] = mapped_column(INTEGER(11), nullable=False, index=True)

    user: Mapped["AuthUser"] = relationship(
        "AuthUser", back_populates="auth_user_groups"
    )


class AuthRegistration(Base):
    """Model for the `auth_registration` table."""

    __tablename__ = "auth_registration"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
        ),
    )
    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    user_id: Mapped[int] = mapped_column(INTEGER(11))
    activation_key: Mapped[int] = mapped_column(String(32), nullable=False, unique=True)

    user: Mapped["AuthUser"] = relationship(
        "AuthUser", back_populates="auth_registration"
    )


class AuthtokenToken(Base):
    """Model for the `authtoken_token` table."""

    __tablename__ = "authtoken_token"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
        ),
    )
    key: Mapped[str] = mapped_column(String(40), primary_key=True)
    user_id: Mapped[int] = mapped_column(INTEGER(11))
    created: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False)

    user: Mapped["AuthUser"] = relationship(
        "AuthUser", back_populates="authtoken_token"
    )


class AuthUserprofile(Base):
    """Model for the `auth_userprofile` table."""

    __tablename__ = "auth_userprofile"
    __table_args__ = (
        ForeignKeyConstraint(
            ["user_id"],
            ["auth_user.id"],
            name="user_id_refs_id_3daaa960628b4c11",
        ),
        Index("auth_userprofile_52094d6e", "name"),
        Index("auth_userprofile_551e365c", "level_of_education"),
        Index("auth_userprofile_8a7ac9ab", "language"),
        Index("auth_userprofile_b54954de", "location"),
        Index("auth_userprofile_d85587", "year_of_birth"),
        Index("auth_userprofile_fca3d292", "gender"),
        Index("user_id", "user_id", unique=True),
    )

    id: Mapped[int] = mapped_column(INTEGER(11), primary_key=True)
    user_id: Mapped[int] = mapped_column(INTEGER(11))
    name: Mapped[str] = mapped_column(String(255))
    language: Mapped[str] = mapped_column(String(255))
    location: Mapped[str] = mapped_column(String(255))
    meta: Mapped[str] = mapped_column(TEXT)
    courseware: Mapped[str] = mapped_column(String(255))
    allow_certificate: Mapped[int] = mapped_column(INTEGER(1))
    gender: Mapped[Optional[str]] = mapped_column(String(6))
    mailing_address: Mapped[Optional[str]] = mapped_column(TEXT)
    year_of_birth: Mapped[Optional[int]] = mapped_column(INTEGER(11))
    level_of_education: Mapped[Optional[str]] = mapped_column(String(6))
    goals: Mapped[Optional[str]] = mapped_column(TEXT)
    country: Mapped[Optional[str]] = mapped_column(String(2))
    city: Mapped[Optional[str]] = mapped_column(TEXT)
    bio: Mapped[Optional[str]] = mapped_column(String(3000))
    profile_image_uploaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime
    )

    user: Mapped["AuthUser"] = relationship(
        "AuthUser", back_populates="auth_userprofile"
    )

    student_languageproficiency: Mapped[List["StudentLanguageproficiency"]] = (
        relationship(
            "StudentLanguageproficiency",
            back_populates="user_profile",
            cascade="all, delete-orphan",
        )
    )
