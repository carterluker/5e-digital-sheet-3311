import hashlib
import hmac
import secrets
from datetime import timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .models import AuthToken, User, as_utc, utcnow

_SCRYPT = dict(n=2**14, r=8, p=1, dklen=32)


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.scrypt(password.encode(), salt=salt, **_SCRYPT)
    return f"scrypt${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, salt, digest = stored.split("$")
        candidate = hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), **_SCRYPT)
        return hmac.compare_digest(candidate, bytes.fromhex(digest))
    except ValueError:
        return False


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def issue_token(db: Session, user: User) -> str:
    """Create an opaque bearer token. Only its hash is stored."""
    token = secrets.token_urlsafe(32)
    db.add(
        AuthToken(
            token_hash=_hash_token(token),
            user_id=user.id,
            expires_at=utcnow() + timedelta(hours=settings.session_ttl_hours),
        )
    )
    return token


def revoke_token(db: Session, token: str) -> None:
    row = db.get(AuthToken, _hash_token(token))
    if row:
        db.delete(row)


_bearer = HTTPBearer(auto_error=False)


def bearer_token(creds: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> str:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated", {"WWW-Authenticate": "Bearer"})
    return creds.credentials


def current_user(token: str = Depends(bearer_token), db: Session = Depends(get_db)) -> User:
    row = db.get(AuthToken, _hash_token(token))
    if row is None or as_utc(row.expires_at) < utcnow():
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token", {"WWW-Authenticate": "Bearer"})
    user = db.get(User, row.user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token", {"WWW-Authenticate": "Bearer"})
    return user


def find_user(db: Session, username: str) -> User | None:
    return db.scalar(select(User).where(User.username == username.lower()))
