from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User
from ..schemas import Credentials, TokenOut, UserOut
from ..security import bearer_token, current_user, find_user, hash_password, issue_token, revoke_token, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Verified against when the username is unknown, so login timing doesn't reveal which names exist.
_DUMMY_HASH = hash_password("not-a-real-password")


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(body: Credentials, db: Session = Depends(get_db)):
    if find_user(db, body.username):
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")
    user = User(username=body.username, password_hash=hash_password(body.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:  # lost a race with a concurrent registration
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Username already taken")
    return user


@router.post("/login", response_model=TokenOut)
def login(body: Credentials, db: Session = Depends(get_db)):
    user = find_user(db, body.username)
    ok = verify_password(body.password, user.password_hash if user else _DUMMY_HASH)
    if not user or not ok:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Incorrect username or password")
    token = issue_token(db, user)
    db.commit()
    return TokenOut(access_token=token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(token: str = Depends(bearer_token), user: User = Depends(current_user), db: Session = Depends(get_db)):
    revoke_token(db, token)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(current_user)):
    return user
