"""Script to populate edX databases with test data.

This script allows generating test data for MySQL and MongoDB databases
used by the edX platform. It creates:
- Users in MySQL
- Course enrollments
- Manual enrollment audits
- Comments and discussion threads in MongoDB

Data is generated consistently between the two databases,
using the same user identifiers.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mongoengine import connect, disconnect

from mork.edx.mongo.factories import CommentFactory, CommentThreadFactory
from mork.conf import settings
from mork.edx.mysql.factories.auth import EdxAuthUserFactory
from mork.edx.mysql.factories.student import EdxStudentCourseenrollmentFactory, EdxStudentManualenrollmentauditFactory
from mork.edx.mysql.factories.base import BaseSQLAlchemyModelFactory, Session, faker
from mork.edx.mysql.models.base import Base


def seed_edx_mysql_database(batch_size: int = 100):
    """Generates and inserts test data into the edX MySQL database.

    This function:
    1. Configures the connection to the MySQL database
    2. Cleans existing tables
    3. Creates test users
    4. Generates course enrollments for each user
    5. Creates manual enrollment audits

    Args:
        batch_size (int): Number of users to create. Default 100.

    Returns:
        list[str]: List of created usernames for use in MongoDB.
    """
    # Database connection configuration
    # We use environment variables defined in docker-compose.yml
    mysql_user = os.getenv('MYSQL_USER', 'edx')
    mysql_password = os.getenv('MYSQL_PASSWORD', 'edx')
    mysql_database = os.getenv('MYSQL_DATABASE', 'edx')
    mysql_url = f'mysql+pymysql://{mysql_user}:{mysql_password}@mysql:3306/{mysql_database}'
    engine = create_engine(mysql_url)
    Session.configure(bind=engine)
    BaseSQLAlchemyModelFactory._meta.sqlalchemy_session = Session  # noqa: SLF001

    # Clean the database before seeding
    # We delete all tables in reverse order of their dependencies
    Base.metadata.drop_all(engine)
    # Recreate empty tables
    Base.metadata.create_all(engine)

    # Create users without related records
    # We disable automatic creation of enrollment audits and course enrollments
    # to avoid foreign key constraint issues
    users = []
    for i in range(batch_size):
        # Generate a unique email for each user
        email = f"{faker.user_name()}{i}@example.com"
        user = EdxAuthUserFactory(
            email=email,
            student_manualenrollmentaudit=None,  # Disable automatic audit creation
            student_courseenrollment=None  # Disable automatic enrollment creation
        )
        users.append(user)
    Session.commit()  # Commit users to the database

    # Create course enrollments for each user
    # We create 3 enrollments per user
    enrollments = []
    for user in users:
        for _ in range(3):
            enrollment = EdxStudentCourseenrollmentFactory(
                user_id=user.id,
                student_manualenrollmentaudit=None  # Disable automatic audit creation
            )
            enrollments.append(enrollment)
    Session.commit()  # Commit enrollments to the database

    # Create manual enrollment audits for each enrollment
    # We create 3 audits per enrollment
    for enrollment in enrollments:
        EdxStudentManualenrollmentauditFactory.create_batch(
            3,
            enrollment_id=enrollment.id,
            enrolled_by_id=enrollment.user_id
        )
    Session.commit()  # Commit audits to the database

    # Get usernames for MongoDB seeding
    usernames = [user.username for user in users]
    return usernames


def seed_edx_mongodb_database(batch_size: int = 1000, usernames: list[str] = []):
    """Generates and inserts test data into the edX MongoDB database.

    This function:
    1. Configures the connection to MongoDB
    2. Cleans existing collections
    3. Creates comments and discussion threads
    4. Associates data with existing users

    Args:
        batch_size (int): Number of comments and discussion threads to create. Default 1000.
        usernames (list[str]): List of usernames to associate with comments.
    """
    # Connect to MongoDB
    # We use the Docker service name 'mongo' as the script runs in a container
    mongo_url = settings.EDX_MONGO_DB_URL.replace('mongo://', 'mongodb://mongo:27017/')
    connect(host=mongo_url)

    # Clean MongoDB collections
    CommentFactory._meta.model.objects.delete()  # noqa: SLF001
    CommentThreadFactory._meta.model.objects.delete()  # noqa: SLF001

    # Create comments and discussion threads
    CommentFactory.create_batch(batch_size, usernames=usernames)
    CommentThreadFactory.create_batch(batch_size, usernames=usernames)

    # Disconnect from MongoDB
    disconnect()


if __name__ == "__main__":
    usernames = seed_edx_mysql_database()
    seed_edx_mongodb_database(usernames=usernames)