"""Module for CRUD functions."""

from datetime import datetime
from logging import getLogger
from typing import Optional

from sqlalchemy import distinct, select, union_all
from sqlalchemy.orm import Session, load_only
from sqlalchemy.sql.functions import count

from mork.edx.models.auth import AuthtokenToken, AuthUser
from mork.edx.models.certificates import (
    CertificatesCertificatehtmlviewconfiguration,
)
from mork.edx.models.contentstore import ContentstoreVideouploadconfig
from mork.edx.models.course import (
    CourseActionStateCoursererunstate,
    CourseCreatorsCoursecreator,
)
from mork.edx.models.dark import DarkLangDarklangconfig
from mork.edx.models.util import UtilRatelimitconfiguration
from mork.edx.models.verify import VerifyStudentHistoricalverificationdeadline
from mork.exceptions import UserDeleteError, UserProtectedDeleteError

logger = getLogger(__name__)


def get_inactive_users_count(
    session: Session,
    threshold_date: datetime,
):
    """Get inactive users count from edx database.

    SELECT count(auth_user.id) FROM auth_user
    """
    query = (
        select(count(distinct(AuthUser.id)))
        .prefix_with("SQL_NO_CACHE", dialect="mysql")
        .filter(AuthUser.last_login < threshold_date)
    )
    return session.execute(query).scalar()


def get_inactive_users(
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
        select(AuthUser)
        .prefix_with("SQL_NO_CACHE", dialect="mysql")
        .options(
            load_only(
                AuthUser.id,
                AuthUser.username,
                AuthUser.email,
                AuthUser.is_staff,
                AuthUser.is_superuser,
                AuthUser.last_login,
            ),
        )
        .filter(AuthUser.last_login < threshold_date)
        .offset(offset)
        .limit(limit)
    )
    return session.scalars(query).unique().all()


def get_user(session: Session, email: str, username: str):
    """Get a user entry based on the provided email and username.

    Parameters:
    session (Session): SQLAlchemy session object.
    email (str): The email of the user to get.
    username (str): The username of the user to get.
    """
    query = select(AuthUser).where(
        AuthUser.email == email, AuthUser.username == username
    )
    return session.execute(query).scalar()


def _has_protected_children(session: Session, user_id) -> bool:
    """Check if user has an entry in a protected children table."""
    union_statement = union_all(
        select(1).where(AuthtokenToken.user_id == user_id),
        select(1).where(
            CertificatesCertificatehtmlviewconfiguration.changed_by_id == user_id
        ),
        select(1).where(ContentstoreVideouploadconfig.changed_by_id == user_id),
        select(1).where(CourseActionStateCoursererunstate.created_user_id == user_id),
        select(1).where(CourseActionStateCoursererunstate.updated_user_id == user_id),
        select(1).where(CourseCreatorsCoursecreator.user_id == user_id),
        select(1).where(DarkLangDarklangconfig.changed_by_id == user_id),
        select(1).where(UtilRatelimitconfiguration.changed_by_id == user_id),
        select(1).where(
            VerifyStudentHistoricalverificationdeadline.history_user_id == user_id
        ),
    )

    # Execute the union query and check if any results exist
    result = session.execute(union_statement).scalars().first()
    return bool(result)


def delete_user(session: Session, email: str, username: str) -> None:
    """Delete a user entry based on the provided email and username.

    Parameters:
    session (Session): SQLAlchemy session object.
    email (str): The email of the user to delete.
    username (str): The username of the user to delete.
    """
    user_to_delete = (
        session.query(AuthUser)
        .filter(AuthUser.email == email, AuthUser.username == username)
        .first()
    )
    if not user_to_delete:
        logger.error(f"No user found with {username=} {email=} for deletion")
        raise UserDeleteError("User to delete does not exist")

    if _has_protected_children(session, user_to_delete.id):
        raise UserProtectedDeleteError(
            "User is linked to a protected table and cannot be deleted"
        )

    session.delete(user_to_delete)
