"""Module for CRUD functions."""

from datetime import datetime
from logging import getLogger
from typing import Optional

from sqlalchemy import delete, distinct, select, union_all
from sqlalchemy.orm import Session, load_only
from sqlalchemy.sql.functions import count

from mork.edx.mysql.models.auth import AuthtokenToken, AuthUser
from mork.edx.mysql.models.certificates import (
    CertificatesCertificatehtmlviewconfiguration,
)
from mork.edx.mysql.models.contentstore import ContentstoreVideouploadconfig
from mork.edx.mysql.models.course import (
    CourseActionStateCoursererunstate,
    CourseCreatorsCoursecreator,
)
from mork.edx.mysql.models.dark import DarkLangDarklangconfig
from mork.edx.mysql.models.student import StudentCourseenrollmentallowed
from mork.edx.mysql.models.util import UtilRatelimitconfiguration
from mork.edx.mysql.models.verify import VerifyStudentHistoricalverificationdeadline
from mork.exceptions import UserNotFound, UserProtected

logger = getLogger(__name__)


def get_inactive_users_count(
    session: Session,
    threshold_date: datetime,
) -> int:
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
) -> list[AuthUser]:
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


def get_user(session: Session, email: str) -> AuthUser:
    """Get a user entry based on the provided email.

    Parameters:
    session (Session): SQLAlchemy session object.
    email (str): The email of the user to get.
    """
    query = select(AuthUser).where(AuthUser.email == email)
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


def delete_user(session: Session, email: str) -> None:
    """Delete a user entry based on the provided email and username.

    Parameters:
    session (Session): SQLAlchemy session object.
    email (str): The email of the user to delete.
    """
    user_to_delete = session.scalar(select(AuthUser).where(AuthUser.email == email))
    if not user_to_delete:
        msg = f"User with {email=} does not exist"
        logger.error(msg)
        raise UserNotFound(msg)

    if _has_protected_children(session, user_to_delete.id):
        msg = f"User with {email=} is linked to a protected table and cannot be deleted"
        logger.error(msg)
        raise UserProtected(msg)

    # Delete entries in student_courseenrollmentallowed table containing user email
    session.execute(
        delete(StudentCourseenrollmentallowed).where(
            StudentCourseenrollmentallowed.email == email
        )
    )

    # Delete user from auth_user table and all its children
    session.delete(user_to_delete)

    logger.debug(f"Deleting user {email=}")
