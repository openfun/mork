"""Tests of the CRUD functions."""

from datetime import datetime, timedelta

import pytest
from faker import Faker

from mork.edx.mysql import crud
from mork.edx.mysql.factories.auth import EdxAuthtokenTokenFactory, EdxAuthUserFactory
from mork.edx.mysql.factories.certificates import (
    EdxCertificatesCertificatehtmlviewconfigurationFactory,
)
from mork.edx.mysql.factories.contentstore import (
    EdxContentstoreVideouploadconfigFactory,
)
from mork.edx.mysql.factories.course import (
    EdxCourseActionStateCoursererunstateFactory,
    EdxCourseCreatorsCoursecreatorFactory,
)
from mork.edx.mysql.factories.dark import EdxDarkLangDarklangconfigFactory
from mork.edx.mysql.factories.student import (
    EdxStudentCourseenrollmentallowedFactory,
)
from mork.edx.mysql.factories.util import EdxUtilRatelimitconfigurationFactory
from mork.edx.mysql.factories.verify import (
    EdxVerifyStudentHistoricalverificationdeadlineFactory,
)
from mork.edx.mysql.models.auth import AuthUser
from mork.edx.mysql.models.base import Base
from mork.exceptions import UserNotFound, UserProtected


def test_edx_crud_get_inactive_users_count(edx_mysql_db):
    """Test the `get_inactive_users_count` method."""
    # 3 users that did not log in for 3 years
    EdxAuthUserFactory.create_batch(
        3, last_login=Faker().date_time_between(end_date="-3y")
    )
    # 4 users that logged in recently
    EdxAuthUserFactory.create_batch(
        4, last_login=Faker().date_time_between(start_date="-3y")
    )

    threshold_date = datetime.now() - timedelta(days=365 * 3)

    # Get count of users inactive for more than 3 years
    users_count = crud.get_inactive_users_count(edx_mysql_db.session, threshold_date)

    assert users_count == 3


def test_edx_crud_get_inactive_users_count_empty(edx_mysql_db):
    """Test the `get_inactive_users_count` method with no inactive users."""
    threshold_date = datetime.now() - timedelta(days=365 * 3)

    # Get count of users inactive for more than 3 years
    users_count = crud.get_inactive_users_count(edx_mysql_db.session, threshold_date)

    assert users_count == 0


def test_edx_crud_get_inactive_users(edx_mysql_db):
    """Test the `get_inactive_users` method."""

    # 3 users that did not log in for 3 years
    inactive_users = EdxAuthUserFactory.create_batch(
        3, last_login=Faker().date_time_between(end_date="-3y")
    )
    # 4 users that logged in recently
    EdxAuthUserFactory.create_batch(
        4, last_login=Faker().date_time_between(start_date="-3y")
    )

    threshold_date = datetime.now() - timedelta(days=365 * 3)

    # Get all users inactive for more than 3 years
    users = crud.get_inactive_users(
        edx_mysql_db.session, threshold_date, offset=0, limit=9
    )

    assert len(users) == 3
    assert users == inactive_users


def test_edx_crud_get_inactive_users_empty(edx_mysql_db):
    """Test the `get_inactive_users` method with no inactive users."""

    threshold_date = datetime.now() - timedelta(days=365 * 3)

    users = crud.get_inactive_users(
        edx_mysql_db.session, threshold_date, offset=0, limit=9
    )

    assert users == []


def test_edx_crud_get_inactive_users_slice(edx_mysql_db):
    """Test the `get_inactive_users` method with a slice."""
    # 3 users that did not log in for 3 years
    inactive_users = EdxAuthUserFactory.create_batch(
        3, last_login=Faker().date_time_between(end_date="-3y")
    )
    # 4 users that logged in recently
    EdxAuthUserFactory.create_batch(
        4, last_login=Faker().date_time_between(start_date="-3y")
    )

    threshold_date = datetime.now() - timedelta(days=365 * 3)

    # Get two users inactive for more than 3 years
    users = crud.get_inactive_users(
        edx_mysql_db.session, threshold_date, offset=0, limit=2
    )

    assert len(users) == 2
    assert users == inactive_users[:2]


def test_edx_crud_get_inactive_users_slice_empty(edx_mysql_db):
    """Test the `get_inactive_users` method with an empty slice ."""
    # 3 users that did not log in for 3 years
    EdxAuthUserFactory.create_batch(
        3, last_login=Faker().date_time_between(end_date="-3y")
    )
    # 4 users that logged in recently
    EdxAuthUserFactory.create_batch(
        4, last_login=Faker().date_time_between(start_date="-3y")
    )

    threshold_date = datetime.now() - timedelta(days=365 * 3)

    users = crud.get_inactive_users(
        edx_mysql_db.session, threshold_date, offset=4, limit=9
    )

    assert users == []


def test_edx_crud_get_user_missing(edx_mysql_db):
    """Test the `get_user` method with missing user in the database."""

    user = crud.get_user(session=edx_mysql_db.session, email="john_doe@example.com")
    assert user is None


def test_edx_crud_get_user(edx_mysql_db):
    """Test the `get_user` method."""
    email = "john_doe@example.com"

    EdxAuthUserFactory.create_batch(1, email=email)

    user = crud.get_user(session=edx_mysql_db.session, email=email)
    assert user.email == email


def test_edx_crud_delete_user_missing(edx_mysql_db):
    """Test the `delete_user` method with missing user in the database."""

    email = "john_doe@example.com"

    with pytest.raises(UserNotFound, match=f"User with {email=} does not exist"):
        crud.delete_user(edx_mysql_db.session, email=email)


def test_edx_crud_delete_user(edx_mysql_db):
    """Test the `delete_user` method."""
    email = "john_doe@example.com"
    EdxAuthUserFactory.create_batch(1, email=email)
    EdxStudentCourseenrollmentallowedFactory.create_batch(3, email=email)

    # Get all related tables that have foreign key constraints on the parent table
    related_tables = [
        "auth_userprofile",
        "auth_user_groups",
        "auth_registration",
        "bulk_email_courseemail",
        "bulk_email_optout",
        "certificates_generatedcertificate",
        "course_groups_courseusergroup_users",
        "course_groups_cohortmembership",
        "courseware_offlinecomputedgrade",
        "courseware_studentmodule",
        "courseware_studentmodulehistory",
        "courseware_xmodulestudentinfofield",
        "courseware_xmodulestudentprefsfield",
        "django_comment_client_role_users",
        "instructor_task_instructortask",
        "notify_settings",
        "payment_useracceptance",
        "proctoru_proctoruexam",
        "proctoru_proctoruuser",
        "student_anonymoususerid",
        "student_courseaccessrole",
        "student_courseenrollment",
        "student_courseenrollmentallowed",
        "student_courseenrollmentattribute",
        "student_historicalcourseenrollment",
        "student_languageproficiency",
        "student_loginfailures",
        "student_manualenrollmentaudit",
        "student_pendingemailchange",
        "student_userstanding",
        "user_api_userpreference",
        "verify_student_softwaresecurephotoverification",
    ]

    for table_name in related_tables:
        table = Base.metadata.tables[table_name]
        assert edx_mysql_db.session.query(table).count() > 0

    crud.delete_user(edx_mysql_db.session, email="john_doe@example.com")

    # Ensure the parent table is empty
    assert edx_mysql_db.session.query(AuthUser).count() == 0

    # Ensure the deletion has cascaded properly on children table
    for table_name in related_tables:
        table = Base.metadata.tables[table_name]
        assert edx_mysql_db.session.query(table).count() == 0


def test_edx_crud_delete_user_protected_table(edx_mysql_db):
    """Test the `delete_user` method on a user with entries in a protected tables."""
    email = "john_doe@example.com"
    EdxAuthUserFactory.create_batch(
        1,
        email=email,
        with_protected_tables=True,
    )

    # Get all related tables that have foreign key constraints on the parent table
    protected_tables = [
        "authtoken_token",
        "certificates_certificatehtmlviewconfiguration",
        "contentstore_videouploadconfig",
        "course_action_state_coursererunstate",
        "course_creators_coursecreator",
        "dark_lang_darklangconfig",
        "util_ratelimitconfiguration",
        "verify_student_historicalverificationdeadline",
    ]

    for table_name in protected_tables:
        table = Base.metadata.tables[table_name]
        assert edx_mysql_db.session.query(table).count() > 0

    with pytest.raises(
        UserProtected,
        match=f"User with {email=} is linked to a protected table and cannot be deleted",  # noqa: E501
    ):
        crud.delete_user(edx_mysql_db.session, email=email)

    # Ensure the parent table is empty
    assert edx_mysql_db.session.query(AuthUser).count() > 0

    # Ensure the deletion has not cascaded on any protected children table
    for table_name in protected_tables:
        table = Base.metadata.tables[table_name]
        assert edx_mysql_db.session.query(table).count() > 0


def test_edx_crud_has_protected_children(edx_mysql_db):
    """Test the `_has_protected_children` method."""
    id = 123
    EdxAuthtokenTokenFactory.create(user_id=id)
    EdxCertificatesCertificatehtmlviewconfigurationFactory.create(changed_by_id=id)
    EdxContentstoreVideouploadconfigFactory.create(changed_by_id=id)
    EdxCourseActionStateCoursererunstateFactory.create(created_user_id=id)
    EdxCourseActionStateCoursererunstateFactory.create(updated_user_id=id)
    EdxCourseCreatorsCoursecreatorFactory.create(user_id=id)
    EdxDarkLangDarklangconfigFactory.create(changed_by_id=id)
    EdxUtilRatelimitconfigurationFactory.create(changed_by_id=id)
    EdxVerifyStudentHistoricalverificationdeadlineFactory.create(history_user_id=id)

    user_id = 456
    assert not crud._has_protected_children(edx_mysql_db.session, user_id)

    EdxCourseActionStateCoursererunstateFactory.create(updated_user_id=user_id)

    assert crud._has_protected_children(edx_mysql_db.session, user_id)
