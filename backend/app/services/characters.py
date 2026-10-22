from fastapi import Depends, HTTPException, status

from ..db.db import get_db

from ..models.Character import Character
from ..models.User import User

from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session


def get_user_characters(user: User, db: Session = Depends(get_db)) -> list[Character]:
    """Retrieves every Character owned by the given user, ordered by name."""

    try:
        return list(db.execute(
            select(Character).where(Character.user_id == user.id).order_by(Character.name)
        ).scalars().all())
    except OperationalError:
        # Database is down or timed out: 503
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The backend database is unavailable."
        )
