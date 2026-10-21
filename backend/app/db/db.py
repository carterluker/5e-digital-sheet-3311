from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from ..config import settings

class ModelBase(DeclarativeBase):
    """DeclarativeBase subclass for model registry."""
    pass

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args={"connect_timeout": settings.database_connect_timeout},
)

SessionLocal = sessionmaker(bind=engine, autoflush=False)

def create_tables():
    """Creates tables for each model registered under the ModelBase class."""

    ModelBase.metadata.create_all(engine)


def get_db() -> Iterator[Session]:
    """Opens a yields a database session as a context manager. Does not commit changes."""
    
    with SessionLocal() as session:
        yield session