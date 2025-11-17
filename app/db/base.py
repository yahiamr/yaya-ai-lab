"""
Database base class and metadata.

- Defines the Declarative ORM Base that all models will inherit from.
- This Base holds the SQLAlchemy metadata used for table creation and migrations.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all ORM models.

    Any model that maps to a database table should inherit from this class.
    SQLAlchemy uses the metadata on this Base to create tables and to
    introspect the schema for tools like Alembic.
    """

    pass