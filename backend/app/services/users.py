from argon2 import PasswordHasher

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from ..config import settings
from ..db.db import create_tables, get_db

from ..models.User import User

from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session


def get_user(username: str, db: Session = Depends(get_db)) -> User | None:
    """Retrieves the record from the User table with the matching username. If no matching user exists, None is returned."""

    # Get User record
    try:
        users = db.execute(select(User).where(User.username == username)).scalars().all() # Get ORM object
    except OperationalError:
        # Database is down or timed out: 503
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The backend database is unavailable."
        )

    if len(users) >= 2:
        # Something has gone horribly wrong. Usernames must be unique.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="More than one user exists with this username."
        )

    if len(users) <= 0:
        # User does not exist under provided username.
        return None
    else:
        return users[0]


def update_user_password_hash(username: str, password: str, db: Session = Depends(get_db)) -> None:
    """Hashes the given password and stores it as the password hash of the user with the matching username."""

    user = get_user(username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No user exists with that username."
        )

    user.password_hash = PasswordHasher().hash(password)

    try:
        db.commit()
    except OperationalError:
        # Database is down or timed out: 503
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The backend database is unavailable."
        )


def login(username: str, password: str, db: Session = Depends(get_db)):
    """Validates the user's credentials and returns a session token."""

    if (user := get_user(username, db)) is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No user exists with that username.",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # Password Hashing
    ph = PasswordHasher()
    try:
        ph.verify(user.password_hash, password)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if the hash parameters are out of date, and update if needed.
    if ph.check_needs_rehash(user.password_hash):
        update_user_password_hash(username, password, db)