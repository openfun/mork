"""Module for defining sessions classes."""

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session, load_only


class UserMixin:
    """Mixin that adds convenience methods for the User operations."""

    @classmethod
    def get_inactives(
        cls,
        session: Session,
        inactivity_period: timedelta,
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
        threshold_date = datetime.now() - inactivity_period

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
