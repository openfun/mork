"""Tests of the mixins class."""

from datetime import datetime, timedelta

from faker import Faker

from mork.edx.factories import EdxUserFactory
from mork.edx.models import User


def test_edx_usermixin_get_inactive_users_count(edx_db):
    """Test the `get_inactive_users_count` method."""
    # 3 users that did not log in for 3 years
    EdxUserFactory.create_batch(3, last_login=Faker().date_time_between(end_date="-3y"))
    # 4 users that logged in recently
    EdxUserFactory.create_batch(
        4, last_login=Faker().date_time_between(start_date="-3y")
    )

    threshold_date = datetime.now() - timedelta(days=365 * 3)

    # Get count of users inactive for more than 3 years
    users_count = User.get_inactive_users_count(edx_db.session, threshold_date)

    assert users_count == 3


def test_edx_usermixin_get_inactive_users_count_empty(edx_db):
    """Test the `get_inactive_users_count` method with no inactive users."""
    threshold_date = datetime.now() - timedelta(days=365 * 3)

    # Get count of users inactive for more than 3 years
    users_count = User.get_inactive_users_count(edx_db.session, threshold_date)

    assert users_count == 0


def test_edx_usermixin_get_inactive_users(edx_db):
    """Test the `get_inactive_users` method."""

    # 3 users that did not log in for 3 years
    inactive_users = EdxUserFactory.create_batch(
        3, last_login=Faker().date_time_between(end_date="-3y")
    )
    # 4 users that logged in recently
    EdxUserFactory.create_batch(
        4, last_login=Faker().date_time_between(start_date="-3y")
    )

    threshold_date = datetime.now() - timedelta(days=365 * 3)

    # Get all users inactive for more than 3 years
    users = User.get_inactive_users(edx_db.session, threshold_date, offset=0, limit=9)

    assert len(users) == 3
    assert users == inactive_users


def test_edx_usermixin_get_inactive_users_empty(edx_db):
    """Test the `get_inactive_users` method with no inactive users."""

    threshold_date = datetime.now() - timedelta(days=365 * 3)

    users = User.get_inactive_users(edx_db.session, threshold_date, offset=0, limit=9)

    assert users == []


def test_edx_usermixin_get_inactive_users_slice(edx_db):
    """Test the `get_inactive_users` method with a slice."""
    # 3 users that did not log in for 3 years
    inactive_users = EdxUserFactory.create_batch(
        3, last_login=Faker().date_time_between(end_date="-3y")
    )
    # 4 users that logged in recently
    EdxUserFactory.create_batch(
        4, last_login=Faker().date_time_between(start_date="-3y")
    )

    threshold_date = datetime.now() - timedelta(days=365 * 3)

    # Get two users inactive for more than 3 years
    users = User.get_inactive_users(edx_db.session, threshold_date, offset=0, limit=2)

    assert len(users) == 2
    assert users == inactive_users[:2]


def test_edx_usermixin_get_inactive_users_slice_empty(edx_db):
    """Test the `get_inactive_users` method with an empty slice ."""
    # 3 users that did not log in for 3 years
    EdxUserFactory.create_batch(3, last_login=Faker().date_time_between(end_date="-3y"))
    # 4 users that logged in recently
    EdxUserFactory.create_batch(
        4, last_login=Faker().date_time_between(start_date="-3y")
    )

    threshold_date = datetime.now() - timedelta(days=365 * 3)

    users = User.get_inactive_users(edx_db.session, threshold_date, offset=4, limit=9)

    assert users == []
