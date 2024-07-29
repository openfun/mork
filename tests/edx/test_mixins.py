"""Tests of the mixins class."""

from datetime import timedelta

from faker import Faker

from mork.edx.factories import EdxUserFactory
from mork.edx.models import User


def test_edx_usermixin_get_inactives(db):
    """Test the `get_inactives` method."""
    # 3 users that did not log in for 3 years
    inactive_users = EdxUserFactory.create_batch(
        3, last_login=Faker().date_time_between(end_date="-3y")
    )
    # 4 users that logged in recently
    EdxUserFactory.create_batch(
        4, last_login=Faker().date_time_between(start_date="-3y")
    )

    # Get all users inactive for more than 3 years
    users = User.get_inactives(
        db.session, inactivity_period=timedelta(days=365 * 3), offset=0, limit=9
    )

    assert len(users) == 3
    assert users == inactive_users


def test_edx_usermixin_get_inactives_empty(db):
    """Test the `get_inactives` method with no inactive users."""

    users = User.get_inactives(
        db.session, inactivity_period=timedelta(days=365 * 3), offset=0, limit=9
    )

    assert users == []


def test_edx_usermixin_get_inactives_slice(db):
    """Test the `get_inactives` method with a slice."""
    # 3 users that did not log in for 3 years
    inactive_users = EdxUserFactory.create_batch(
        3, last_login=Faker().date_time_between(end_date="-3y")
    )
    # 4 users that logged in recently
    EdxUserFactory.create_batch(
        4, last_login=Faker().date_time_between(start_date="-3y")
    )

    # Get two users inactive for more than 3 years
    users = User.get_inactives(
        db.session, inactivity_period=timedelta(days=365 * 3), offset=0, limit=2
    )

    assert len(users) == 2
    assert users == inactive_users[:2]


def test_edx_usermixin_get_inactives_slice_empty(db):
    """Test the `get_inactives` method with an empty slice ."""
    # 3 users that did not log in for 3 years
    EdxUserFactory.create_batch(3, last_login=Faker().date_time_between(end_date="-3y"))
    # 4 users that logged in recently
    EdxUserFactory.create_batch(
        4, last_login=Faker().date_time_between(start_date="-3y")
    )

    users = User.get_inactives(
        db.session, inactivity_period=timedelta(days=365 * 3), offset=4, limit=9
    )

    assert users == []
