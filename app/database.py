"""
Database Configuration and Session Management

SQLAlchemy converts Python classes to PostgreSQL tables automatically.
We NEVER write raw SQL - everything is done through SQLAlchemy ORM.

PRIMARY method for creating tables: alembic upgrade head
BACKUP method: create_tables.py
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator
from app.config import settings

# Create database engine
# echo=True shows SQL queries in console (useful for debugging)
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # Shows SQL in console when DEBUG=True
    pool_pre_ping=True,  # Checks connection before using from pool
    pool_size=10,  # Maximum number of connections in pool
    max_overflow=20  # Extra connections beyond pool_size
)

# Session factory for creating database sessions
# autocommit=False: Changes must be explicitly committed
# autoflush=False: Changes not auto-flushed to database
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models - all models inherit from this
Base = declarative_base()


def get_db() -> Generator:
    """
    Dependency injection for database sessions.
    Creates a new session for each request and closes it after.

    Usage in FastAPI endpoints:
        @router.get("/")
        def endpoint(db: Session = Depends(get_db)):
            # Use db session here
            pass

    Yields:
        Session: SQLAlchemy database session
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()  # Commit any pending changes
    except Exception:
        db.rollback()  # Rollback on error
        raise
    finally:
        db.close()  # Always close the session