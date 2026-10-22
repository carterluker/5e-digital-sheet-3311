from collections.abc import Iterator

from ..models.ModelBase import ModelBase

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, sessionmaker

from ..config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    connect_args={"connect_timeout": settings.database_connect_timeout},
)

def create_tables():
    """Creates tables for each model registered under the ModelBase class."""

    try:
        ModelBase.metadata.create_all(engine)
    except OperationalError:
        # Database is down or timed out: 503
        raise TimeoutError("Database connection timed out. Could not create/validate database tables.")

SessionLocal = sessionmaker(bind=engine, autoflush=False)

def get_db() -> Iterator[Session]:
    """Yields a database session, closing it when the caller is done. Does not commit changes.

    This is a GENERATOR, so it must not be called directly (that returns a generator, not a
    Session). Use it as a FastAPI dependency, which runs it and injects the session:

        def endpoint(db: Session = Depends(get_db)): ...
    """

    with SessionLocal() as session:
        yield session