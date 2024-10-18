"""Mork edx MongoDB database connection."""

from pymongo import MongoClient

from mork.conf import settings


class OpenEdxMongoDB:
    """Class to connect to the Open edX MongoDB database."""

    session = None

    def __init__(self):
        """Instantiate the MongoDB client."""
        self.client = MongoClient(settings.EDX_MONGO_DB_URL)
        self.database = self.client[settings.EDX_MONGO_DB_NAME]
        self.collection = self.database["contents"]
