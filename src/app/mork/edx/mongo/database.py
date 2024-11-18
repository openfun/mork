"""Mork edx MongoDB database connection."""

from mongoengine import connect, disconnect

from mork.conf import settings


class OpenEdxMongoDB:
    """Class to connect to the Open edX MongoDB database."""

    connection = None

    def __init__(self, connection=None):
        """Instantiate the MongoDB connection."""
        if connection is not None:
            self.connection = connection
        else:
            self.connection = connect(
                host=settings.EDX_MONGO_DB_HOST,
                username=settings.EDX_MONGO_DB_USER,
                password=settings.EDX_MONGO_DB_PASSWORD,
                db=settings.EDX_MONGO_DB_NAME,
            )

    def disconnect(self):
        """Close the connection with MongoDB."""
        disconnect()
