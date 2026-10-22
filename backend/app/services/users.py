import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from ..config import settings
from ..db.db import create_tables, get_db

from ..models.User import User
from ..models.UserSession import UserSession

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, OperationalError
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


def create_user(username: str, password: str, db: Session = Depends(get_db)) -> User:
    """Hashes the given password and creates a new User record with the given username. Returns the created user."""

    if get_user(username, db) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user already exists with that username."
        )

    user = User(
        username=username,
        password_hash=PasswordHasher().hash(password),
        created_date=datetime.now(timezone.utc)
    )

    try:
        db.add(user)
        db.commit()
    except IntegrityError:
        # Another request created this username after the check above. Usernames must be unique.
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user already exists with that username."
        )
    except OperationalError:
        # Database is down or timed out: 503
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The backend database is unavailable."
        )

    return user


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


def create_user_session(user_id: int, db: Session = Depends(get_db)) -> str:
    """Creates a UserSession record for the given user and returns the session token."""

    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)

    user_session = UserSession(
        user_id=user_id,
        token_hash=hashlib.sha256(token.encode()).hexdigest(),
        created_date=now,
        expires_date=now + timedelta(hours=settings.session_lifetime_hours)
    )

    try:
        db.add(user_session)
        db.commit()
    except IntegrityError:
        # The user_id does not reference an existing user (or, miraculously, the token collided).
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Could not create a session for that user."
        )
    except OperationalError:
        # Database is down or timed out: 503
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The backend database is unavailable."
        )

    return token


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

    return create_user_session(user.id, db)