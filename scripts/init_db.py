"""
CLI entrypoint for initializing the database schema.

Usage:
    python scripts/init_db.py
"""

from app.db.base import Base
from app.db.session import engine
from app import models  # noqa: F401  -> ensures models are imported


def init_db() -> None:
    """
    Create all tables defined on Base.metadata if they do not exist.
    """
    # Import side effects from app.models ensure all models are registered.
    _ = models  # noqa: F841

    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()