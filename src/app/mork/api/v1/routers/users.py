"""User-related API routes.

This module handles user retrieval, modification, and status tracking.

- User search by email in edx (MySQL) and Mork (PostgreSQL)
- Deletion status management by service
- Endpoints for reading and updating statuses
"""

import logging
from dataclasses import dataclass
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from mork.auth import authenticate_api_key
from mork.db import get_session
from mork.models.users import (
    ServiceName,
    User,
    UserServiceStatus,
)
from mork.schemas.users import (
    DeletionStatus,
    UserRead,
    UserStatusRead,
    UserStatusUpdate,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/users", dependencies=[Depends(authenticate_api_key)])


@dataclass
class UserQueryParams:
    """Query parameters for user filtering."""
    email: str | None = None
    username: str | None = None
    offset: int = 0
    limit: int = 100


def _build_user_query(params: UserQueryParams) -> select:
    """Build the SQLAlchemy query based on filter parameters."""
    statement = select(User)

    # Add email filter
    if params.email:
        statement = statement.where(User.email.ilike(f"%{params.email}%"))

    # Add username filter
    if params.username:
        statement = statement.where(User.username.ilike(f"%{params.username}%"))

    return statement.offset(params.offset).limit(params.limit)


def _parse_user_id(user_id: str) -> tuple[bool, bool]:
    """Parse user_id to determine if it's an email or UUID."""
    if '@' in user_id:
        return True, False

    try:
        UUID(user_id)
        return False, True
    except ValueError:
        return '@' in user_id, False


def _build_user_statement(
    user_id: str,
    is_email: bool,
    is_uuid: bool,
    exclude_deleted: bool
) -> select:
    """Build the appropriate query statement for user lookup."""
    if is_email:
        statement = select(User).where(User.email == user_id)
    elif is_uuid:
        statement = select(User).where(User.id == UUID(user_id))
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user_id format"
        ) from None

    if exclude_deleted:
        statement = statement.join(UserServiceStatus).where(
            UserServiceStatus.status.notin_([
                DeletionStatus.TO_DELETE,
                DeletionStatus.DELETING,
                DeletionStatus.DELETED
            ])
        )

    return statement


@router.get("")
@router.get("/")
async def read_users(
    session: Annotated[Session, Depends(get_session)],
    email: Annotated[
        str | None,
        Query(description="Filter users by email"),
    ] = None,
    username: Annotated[
        str | None,
        Query(description="Filter users by username"),
    ] = None,
    offset: Annotated[
        int | None,
        Query(ge=0, description="Number of elements to skip"),
    ] = 0,
    limit: Annotated[
        int | None,
        Query(le=1000, description="Maximum number of elements to retrieve"),
    ] = 100,
) -> list[UserRead]:
    """Retrieves a list of users based on query parameters.

    Allows filtering by email and username with partial matching.
    """
    params = UserQueryParams(
        email=email,
        username=username,
        offset=offset,
        limit=limit,
    )

    statement = _build_user_query(params)
    users = session.scalars(statement).unique().all()

    response_users = [UserRead.model_validate(user) for user in users]
    logger.debug("Results = %s", response_users)
    return response_users


@router.get("/{user_id}")
async def read_user(
    session: Annotated[Session, Depends(get_session)],
    user_id: Annotated[str, Path(description="User ID or email to read")],
    exclude_deleted: Annotated[
        bool,
        Query(description="Exclude users with deletion statuses"),
    ] = True,
) -> UserRead:
    """Retrieves a user by their ID or email.

    If exclude_deleted is True, will not return users with deletion statuses:
    TO_DELETE, DELETING, DELETED.
    """
    is_email, is_uuid = _parse_user_id(user_id)
    statement = _build_user_statement(user_id, is_email, is_uuid, exclude_deleted)
    user = session.scalar(statement)

    if not user:
        message = "User not found"
        if exclude_deleted:
            message += " or user is deleted/being processed"
        logger.debug("%s: %s", message, user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

    response_user = UserRead.model_validate(user)
    logger.debug("Result = %s", response_user)
    return response_user


@router.get("/{user_id}/status/{service_name}")
async def read_user_status(
    session: Annotated[Session, Depends(get_session)],
    user_id: Annotated[str, Path(description="User ID to read the status")],
    service_name: Annotated[
        ServiceName,
        Path(description="Service name making the request"),
    ],
) -> UserStatusRead:
    """Retrieves the deletion status of a user for a given service."""
    # Convert string user_id to UUID
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid user ID format"
        ) from None

    statement = select(UserServiceStatus).where(
        UserServiceStatus.user_id == user_uuid,
        UserServiceStatus.service_name == service_name,
    )

    service_status = session.scalar(statement)

    if not service_status:
        message = "User status not found"
        logger.debug("%s: %s %s", message, user_id, service_name)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

    response = UserStatusRead(
        id=service_status.user_id,
        service_name=service_status.service_name,
        status=service_status.status,
    )
    logger.debug("Results = %s", response)

    return response


@router.patch("/{user_id}/status/{service_name}")
async def update_user_status(
    session: Annotated[Session, Depends(get_session)],
    user_id: Annotated[str, Path(title="User ID to update")],
    service_name: Annotated[
        ServiceName,
        Path(description="Service name to update the status"),
    ],
    deletion_status: Annotated[
        DeletionStatus,
        Body(description="New deletion status", embed=True),
    ],
) -> UserStatusUpdate:
    """Updates the deletion status of a user for a given service."""
    # Convert string user_id to UUID
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid user ID format"
        ) from None

    statement = (
        update(UserServiceStatus)
        .where(
            UserServiceStatus.user_id == user_uuid,
            UserServiceStatus.service_name == service_name,
        )
        .values(status=deletion_status)
        .returning(UserServiceStatus)
    )

    try:
        updated = session.execute(statement).scalars().one()
    except NoResultFound as exc:
        message = "User status not found"
        logger.debug("%s: %s", message, user_id)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=message
        ) from exc

    session.commit()

    response_user = UserStatusUpdate(
        id=updated.user_id,
        service_name=updated.service_name,
        status=updated.status,
    )
    logger.debug("Results = %s", response_user)

    return response_user
