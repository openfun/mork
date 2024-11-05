"""API routes related to users."""

import logging
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


@router.get("")
@router.get("/")
async def read_users(
    session: Annotated[Session, Depends(get_session)],
    service: Annotated[
        ServiceName | None,
        Query(description="The name of the service to filter users on"),
    ] = None,
    deletion_status: Annotated[
        DeletionStatus | None,
        Query(description="The deletion status to filter users on"),
    ] = None,
    offset: Annotated[
        int | None,
        Query(ge=0, description="The number of items to offset"),
    ] = 0,
    limit: Annotated[
        int | None,
        Query(le=1000, description="The maximum number of items to retrieve"),
    ] = 100,
) -> list[UserRead]:
    """Retrieve a list of users based on the query parameters."""
    statement = select(User)

    if service or deletion_status:
        statement = statement.join(UserServiceStatus)

    if service:
        statement = statement.where(UserServiceStatus.service_name == service)

    if deletion_status:
        statement = statement.where(UserServiceStatus.status == deletion_status)

    users = session.scalars(statement.offset(offset).limit(limit)).unique().all()

    response_users = [UserRead.model_validate(user) for user in users]
    logger.debug("Results = %s", response_users)
    return response_users


@router.get("/{user_id}")
async def read_user(
    session: Annotated[Session, Depends(get_session)],
    user_id: Annotated[UUID, Path(description="The id of the user to read")],
    service: Annotated[
        ServiceName | None,
        Query(description="The name of the service to filter users on"),
    ] = None,
) -> UserRead:
    """Retrieve the user from its id."""
    statement = select(User).where(User.id == user_id)

    if service:
        statement = statement.join(UserServiceStatus).where(
            UserServiceStatus.service_name == service
        )

    user = session.scalar(statement)

    if not user:
        message = "User not found"
        logger.debug("%s: %s", message, user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

    response_user = UserRead.model_validate(user)
    logger.debug("Result = %s", response_user)
    return response_user


@router.get("/{user_id}/status/{service_name}")
async def read_user_status(
    session: Annotated[Session, Depends(get_session)],
    user_id: Annotated[
        UUID, Path(description="The ID of the user to read status from")
    ],
    service_name: Annotated[
        ServiceName,
        Path(description="The name of the service making the request"),
    ],
) -> UserStatusRead:
    """Read the user deletion status for a specific service."""
    statement = select(UserServiceStatus).where(
        UserServiceStatus.user_id == user_id,
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
    user_id: Annotated[UUID, Path(title="The ID of the user to update status")],
    service_name: Annotated[
        ServiceName,
        Path(description="The name of the service to update status"),
    ],
    deletion_status: Annotated[
        DeletionStatus,
        Body(description="The new deletion status", embed=True),
    ],
) -> UserStatusUpdate:
    """Update the user deletion status for a specific service."""
    statement = (
        update(UserServiceStatus)
        .where(
            UserServiceStatus.user_id == user_id,
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

    response_user = UserStatusUpdate(
        id=updated.user_id,
        service_name=updated.service_name,
        status=updated.status,
    )
    logger.debug("Results = %s", response_user)

    return response_user
