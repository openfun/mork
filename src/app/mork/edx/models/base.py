"""Mork edx models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all models in the database."""

    filtered_attrs = []

    def safe_dict(self):
        """Return a dictionary representation of the model."""
        return {
            c.name: getattr(self, c.name)
            for c in self.__table__.columns
            if c.name not in self.filtered_attrs
        }
