from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from ..config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)

def create_db_and_tables():
    """TODO: Create db and tables on startup"""
    raise NotImplementedError


def get_db() -> Iterator[Session]:
    """Opens a yields a database session as a context manager. Does not commit changes."""
    
    with SessionLocal() as session:
        yield session