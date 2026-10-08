from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import DATABASE_URL

# The engine manages the connection pool used to talk to PostgreSQL.
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# A Session is a short-lived unit of work used by one API request at a time.
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Parent class that SQLAlchemy uses to collect database table definitions."""


def get_db() -> Generator[Session, None, None]:
    """Give an endpoint a session and always close it when the request finishes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
