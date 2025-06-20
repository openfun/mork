"""User-related API routes.

This module handles user retrieval, modification, and status tracking.

- User search by email in edx (MySQL) and Mork (PostgreSQL)
- Deletion status management by service
- Endpoints for reading and updating statuses
"""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from sqlalchemy import select, update
from sqlalchemy.exc import NoResultFound, OperationalError
from sqlalchemy.orm import Session

from mork.auth import authenticate_api_key
from mork.db import get_session
from mork.edx.mysql.database import OpenEdxMySQLDB
from mork.edx.mysql.models.auth import AuthUser
from mork.models.users import (
    ServiceName,
    User,
    UserServiceStatus,
)
from mork.models.users import User as MorkUser
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
        Query(description="Service name to filter users"),
    ] = None,
    deletion_status: Annotated[
        DeletionStatus | None,
        Query(description="Deletion status to filter users"),
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

    Allows filtering by service and deletion status.
    """
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
    user_id: Annotated[UUID, Path(description="User ID to read")],
    service: Annotated[
        ServiceName | None,
        Query(description="Service name to filter the user"),
    ] = None,
) -> UserRead:
    """Retrieves a user by their ID (and optionally by service)."""
    statement = select(User).where(User.id == user_id)

    if service:
        statement = statement.join(UserServiceStatus).where(
            UserServiceStatus.service_name == service
        )

    user = session.scalar(statement)

    if not user:
        # test
        message = "User not found"
        logger.debug("%s: %s", message, user_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)

    response_user = UserRead.model_validate(user)
    logger.debug("Result = %s", response_user)
    return response_user


@router.get("/{user_id}/status/{service_name}")
async def read_user_status(
    session: Annotated[Session, Depends(get_session)],
    user_id: Annotated[UUID, Path(description="User ID to read the status")],
    service_name: Annotated[
        ServiceName,
        Path(description="Service name making the request"),
    ],
) -> UserStatusRead:
    """Retrieves the deletion status of a user for a given service."""
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
    user_id: Annotated[UUID, Path(title="User ID to update")],
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

    session.commit()

    response_user = UserStatusUpdate(
        id=updated.user_id,
        service_name=updated.service_name,
        status=updated.status,
    )
    logger.debug("Results = %s", response_user)

    return response_user


@router.get("/by-email/", status_code=200)
async def get_user_by_email(
    email: str = Query(..., description="User email to search for"),
    session: Session = Depends(get_session),
) -> dict:
    """Searches for a user by email and returns.

    - edx info (id, username, first_name, last_name, email, etc.)
    - Mork deletion status (service_statuses)
    """
    # --- Search in edx (MySQL) ---
    edx_user = None
    try:
        edx_mysql_db = OpenEdxMySQLDB()
        edx_user = edx_mysql_db.session.execute(
            select(AuthUser).where(AuthUser.email == email)
        ).scalar_one_or_none()
        edx_mysql_db.session.close()
    except (ConnectionError, OSError, ValueError, OperationalError) as exc:
        logger.warning(f"Could not connect to edX database for email {email}: {exc}")
        edx_user = None

    # --- Search in Mork (PostgreSQL) ---
    mork_user = session.execute(
        select(MorkUser).where(MorkUser.email == email)
    ).scalar_one_or_none()

    # --- Build response ---
    result = {"email": email}

    if edx_user:
        result["edx_user"] = {
            "id": getattr(edx_user, "id", None),
            "username": getattr(edx_user, "username", None),
            "first_name": getattr(edx_user, "first_name", None),
            "last_name": getattr(edx_user, "last_name", None),
            "is_active": bool(getattr(edx_user, "is_active", False)),
            "date_joined": (
                edx_user.date_joined.isoformat()
                if getattr(edx_user, "date_joined", None)
                else None
            ),
            "last_login": (
                edx_user.last_login.isoformat()
                if getattr(edx_user, "last_login", None)
                else None
            ),
        }
    else:
        result["edx_user"] = None

    if mork_user:
        # Deletion status for each service
        try:
            service_statuses = [
                {
                    "service_name": getattr(
                        s.service_name, "value", str(s.service_name)
                    ),
                    "status": getattr(s.status, "value", str(s.status)),
                }
                for s in getattr(mork_user, "service_statuses", [])
            ]
        except (AttributeError, ValueError) as e:
            logger.error(f"Error retrieving service statuses: {e}")
            service_statuses = []
        created_at = (
            mork_user.created_at.isoformat()
            if getattr(mork_user, "created_at", None)
            else None
        )
        updated_at = (
            mork_user.updated_at.isoformat()
            if getattr(mork_user, "updated_at", None)
            else None
        )
        result["mork_status"] = {
            "id": str(getattr(mork_user, "id", "")),
            "service_statuses": service_statuses,
            "reason": getattr(
                getattr(mork_user, "reason", None),
                "value",
                str(getattr(mork_user, "reason", None)),
            ),
            "created_at": created_at,
            "updated_at": updated_at,
        }
    else:
        result["mork_status"] = None

    # --- If no user found, return 404 ---
    if not edx_user and not mork_user:
        raise HTTPException(status_code=404, detail="No user found for this email.")

    return result
