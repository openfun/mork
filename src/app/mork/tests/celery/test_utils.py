"""Tests for Mork Celery utils."""

import re

from pytest_httpx import HTTPXMock
from sqlalchemy import select

from mork.celery.utils import (
    get_service_status,
    get_user_from_mork,
    update_status_in_mork,
)
from mork.factories.users import UserFactory, UserServiceStatusFactory
from mork.models.users import DeletionStatus, ServiceName, User
from mork.schemas.users import UserRead


def test_get_user_from_mork(db_session, httpx_mock: HTTPXMock):
    """Test the behavior of getting a user from Mork API."""

    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database
    UserFactory.create()

    # Get user from db
    expected_user = UserRead.model_validate(db_session.scalar(select(User)))

    httpx_mock.add_response(
        url=re.compile(rf".*v1/users/{expected_user.id}"),
        method="GET",
        json=expected_user.model_dump(mode="json"),
        status_code=200,
    )

    user = get_user_from_mork(expected_user.id)

    assert user == expected_user


def test_get_user_from_mork_invalid(db_session, httpx_mock: HTTPXMock):
    """Test the behavior of getting a user from Mork with invalid user id or status."""

    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database
    UserFactory.create()

    # Get user from db
    expected_user = UserRead.model_validate(db_session.scalar(select(User)))

    httpx_mock.add_response(
        url=re.compile(rf".*v1/users/{expected_user.id}"),
        method="GET",
        status_code=404,
    )

    assert get_user_from_mork(expected_user.id) is None


def test_get_service_status(db_session, httpx_mock: HTTPXMock):
    """Test the behavior of getting the status from a user."""

    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database
    expected_status = DeletionStatus.DELETED
    UserFactory.create(
        service_statuses={ServiceName.EDX: expected_status},
    )

    # Get user from db
    expected_user = UserRead.model_validate(db_session.scalar(select(User)))

    status = get_service_status(expected_user, ServiceName.EDX)

    assert status == expected_status


def test_get_service_status_not_found(db_session, httpx_mock: HTTPXMock):
    """Test the behavior of getting a inexistent status from a user."""

    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database
    UserFactory.create()

    # Get user from db
    expected_user = UserRead.model_validate(db_session.scalar(select(User)))

    # Remove statuses of the user
    expected_user.service_statuses = []

    status = get_service_status(expected_user, ServiceName.EDX)

    assert status is None


def test_update_status_in_mork(db_session, httpx_mock: HTTPXMock):
    """Test the behavior of updating the user status."""

    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database
    UserFactory.create()

    # Get id of one of the newly created user
    user_id = db_session.scalar(select(User.id))

    service_name = "ashley"

    httpx_mock.add_response(
        url=re.compile(rf".*v1/users/{user_id}/status/{service_name}"),
        method="PATCH",
        status_code=200,
    )

    success = update_status_in_mork(user_id, ServiceName.ASHLEY, DeletionStatus.DELETED)
    assert success


def test_update_user_status_invalid(db_session, httpx_mock: HTTPXMock):
    """Test the behavior of updating the user status with an invalid response."""

    UserServiceStatusFactory._meta.sqlalchemy_session = db_session
    UserFactory._meta.sqlalchemy_session = db_session

    # Create one user in the database
    UserFactory.create()

    # Get id of one of the newly created user
    user_id = db_session.scalar(select(User.id))

    service_name = "ashley"

    httpx_mock.add_response(
        url=re.compile(rf".*v1/users/{user_id}/status/{service_name}"),
        method="PATCH",
        status_code=404,
    )

    success = update_status_in_mork(user_id, ServiceName.ASHLEY, DeletionStatus.DELETED)
    assert not success
