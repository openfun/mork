"""Module for defining sessions classes."""

from datetime import datetime
from logging import getLogger
from typing import Optional

from sqlalchemy import distinct, select
from sqlalchemy.orm import Session, load_only
from sqlalchemy.sql.functions import count

from mork.exceptions import UserDeleteError

logger = getLogger(__name__)


class AuthUserMixin:
    """Mixin that adds convenience methods for the AuthUser operations."""

    @classmethod
    def get_inactive_users_count(
        cls,
        session: Session,
        threshold_date: datetime,
    ):
        """Get inactive users count from edx database.

        SELECT count(auth_user.id) FROM auth_user
        """
        query = (
            select(count(distinct(cls.id)))
            .prefix_with("SQL_NO_CACHE", dialect="mysql")
            .filter(cls.last_login < threshold_date)
        )
        return session.execute(query).scalar()

    @classmethod
    def get_inactive_users(
        cls,
        session: Session,
        threshold_date: datetime,
        offset: Optional[int] = 0,
        limit: Optional[int] = 0,
    ):
        """Get users from edx database who have not logged in for a specified period.

        SELECT auth_user.id,
            auth_user.username,
            auth_user.email,
            auth_user.is_staff,
            auth_user.is_superuser,
            auth_user.last_login,
        FROM auth_user LIMIT :param_1 OFFSET :param_2
        """
        query = (
            select(cls)
            .prefix_with("SQL_NO_CACHE", dialect="mysql")
            .options(
                load_only(
                    cls.id,
                    cls.username,
                    cls.email,
                    cls.is_staff,
                    cls.is_superuser,
                    cls.last_login,
                ),
            )
            .filter(cls.last_login < threshold_date)
            .offset(offset)
            .limit(limit)
        )
        return session.scalars(query).unique().all()

    @classmethod
    def get_user(cls, session: Session, email: str, username: str):
        """Get a user entry based on the provided email and username.

        Parameters:
        session (Session): SQLAlchemy session object.
        email (str): The email of the user to get.
        username (str): The username of the user to get.
        """
        query = select(cls).where(cls.email == email, cls.username == username)
        return session.execute(query).scalar()

    @classmethod
    def delete_user(cls, session: Session, email: str, username: str) -> None:
        """Delete a user entry based on the provided email and username.

        Parameters:
        session (Session): SQLAlchemy session object.
        email (str): The email of the user to delete.
        username (str): The username of the user to delete.
        """
        user_to_delete = (
            session.query(cls)
            .filter(cls.email == email, cls.username == username)
            .first()
        )
        if not user_to_delete:
            logger.error(f"No user found with {username=} {email=} for deletion")
            raise UserDeleteError("User to delete does not exist")

        session.delete(user_to_delete)
