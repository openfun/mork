"""Mork users schemas."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr

from mork.models.users import DeletionReason, DeletionStatus, ServiceName


class UserServiceStatusRead(BaseModel):
    """Model for reading service statuses of a user."""

    model_config = ConfigDict(from_attributes=True)

    service_name: ServiceName
    status: DeletionStatus


class UserRead(BaseModel):
    """Model for reading detailed information about a user."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    edx_user_id: int
    email: EmailStr
    reason: DeletionReason
    service_statuses: list[UserServiceStatusRead]


class UserStatusRead(BaseModel):
    """Model for reading a user status."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    service_name: ServiceName
    status: DeletionStatus


class UserStatusUpdate(BaseModel):
    """Model for response after updating a user status."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    service_name: ServiceName
    status: DeletionStatus
