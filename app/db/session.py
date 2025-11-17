"""
Database engine and session management.

- Creates the SQLAlchemy Engine using the DATABASE_URL from settings.
- Defines a SessionLocal factory for creating Session objects.
- Provides a get_db() dependency for FastAPI routes to obtain a scoped session.
"""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import session,sessionmaker

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger("app.db")

# Create the SQLAlchemy Engine.
# - str(settings.DATABASE_URL) converts AnyUrl to plain string.
# - echo=settings.DEBUG can be useful when debugging SQL queries.
engine = create_engine(
    str(settings.DATABASE_URL),
    echo=settings.DEBUG,
    future=True,  # use SQLAlchemy 2.x style behavior
)

# Create a configurable Session factory.
# Each SessionLocal instance will be a new Session connected to the engine.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    future=True,
)

def get_db() -> Generator[session, None, None]:
    """
    FastAPI dependency that provides a database session.

    Usage in routes:
        from fastapi import Depends
        from sqlalchemy.orm import Session

        @router.get("/items")
        def list_items(db: Session = Depends(get_db)):
            ...

    This function:
    - Opens a new Session.
    - Yields it to the route handler.
    - Ensures the Session is closed after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()