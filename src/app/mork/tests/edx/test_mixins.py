"""Tests of the mixins class."""

from datetime import datetime, timedelta

import pytest
from faker import Faker

from mork.edx.factories.auth import EdxAuthUserFactory
from mork.edx.models.auth import AuthUser
from mork.edx.models.base import Base
from mork.exceptions import UserDeleteError


def test_edx_usermixin_get_inactive_users_count(edx_db):
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
    users_count = AuthUser.get_inactive_users_count(edx_db.session, threshold_date)

    assert users_count == 3


def test_edx_usermixin_get_inactive_users_count_empty(edx_db):
    """Test the `get_inactive_users_count` method with no inactive users."""
    threshold_date = datetime.now() - timedelta(days=365 * 3)

    # Get count of users inactive for more than 3 years
    users_count = AuthUser.get_inactive_users_count(edx_db.session, threshold_date)

    assert users_count == 0


def test_edx_usermixin_get_inactive_users(edx_db):
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
    users = AuthUser.get_inactive_users(
        edx_db.session, threshold_date, offset=0, limit=9
    )

    assert len(users) == 3
    assert users == inactive_users


def test_edx_usermixin_get_inactive_users_empty(edx_db):
    """Test the `get_inactive_users` method with no inactive users."""

    threshold_date = datetime.now() - timedelta(days=365 * 3)

    users = AuthUser.get_inactive_users(
        edx_db.session, threshold_date, offset=0, limit=9
    )

    assert users == []


def test_edx_usermixin_get_inactive_users_slice(edx_db):
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
    users = AuthUser.get_inactive_users(
        edx_db.session, threshold_date, offset=0, limit=2
    )

    assert len(users) == 2
    assert users == inactive_users[:2]


def test_edx_usermixin_get_inactive_users_slice_empty(edx_db):
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

    users = AuthUser.get_inactive_users(
        edx_db.session, threshold_date, offset=4, limit=9
    )

    assert users == []


def test_edx_usermixin__get_user_missing(edx_db):
    """Test the `get_user` method with missing user in the database."""

    user = AuthUser.get_user(
        session=edx_db.session, email="john_doe@example.com", username="john_doe"
    )
    assert user is None


def test_edx_usermixin__get_user(edx_db):
    """Test the `get_user` method."""
    email = "john_doe@example.com"
    username = "john_doe"

    EdxAuthUserFactory.create_batch(1, email=email, username=username)

    user = AuthUser.get_user(session=edx_db.session, email=email, username=username)
    assert user.email == email
    assert user.username == username


def test_edx_usermixin__delete_user_missing(edx_db):
    """Test the `delete_user` method with missing user in the database."""

    with pytest.raises(UserDeleteError, match="User to delete does not exist"):
        AuthUser.delete_user(
            edx_db.session, email="john_doe@example.com", username="john_doe"
        )


def test_edx_usermixin_delete_user(edx_db):
    """Test the `delete_user` method."""
    EdxAuthUserFactory.create_batch(
        1, email="john_doe@example.com", username="john_doe"
    )

    # Get all related tables that have foreign key constraints on the parent table
    related_tables = [
        "course_action_state_coursererunstate",
        "auth_userprofile",
        "authtoken_token",
        "auth_registration",
        "bulk_email_courseemail",
        "bulk_email_optout",
        "certificates_certificatehtmlviewconfiguration",
        "certificates_generatedcertificate",
        "contentstore_videouploadconfig",
        "course_creators_coursecreator",
        "courseware_offlinecomputedgrade",
        "courseware_studentmodule",
        "courseware_xmodulestudentinfofield",
        "courseware_xmodulestudentprefsfield",
        "dark_lang_darklangconfig",
        "instructor_task_instructortask",
        "notify_settings",
        "proctoru_proctoruexam",
        "proctoru_proctoruuser",
        "student_anonymoususerid",
        "student_courseaccessrole",
        "student_courseenrollment",
        "student_historicalcourseenrollment",
        "student_loginfailures",
        "student_pendingemailchange",
        "student_userstanding",
        "user_api_userpreference",
        "util_ratelimitconfiguration",
        "verify_student_historicalverificationdeadline",
    ]

    for table_name in related_tables:
        table = Base.metadata.tables[table_name]
        assert edx_db.session.query(table).count() > 0

    AuthUser.delete_user(
        edx_db.session, email="john_doe@example.com", username="john_doe"
    )

    # Ensure the parent table is empty
    assert edx_db.session.query(AuthUser).count() == 0

    # Ensure the deletion has cascaded properly on children table
    for table_name in related_tables:
        table = Base.metadata.tables[table_name]
        assert edx_db.session.query(table).count() == 0
