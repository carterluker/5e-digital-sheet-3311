from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db.db import SessionLocal, create_tables, get_db

from .models.User import User
from .models.UserSession import UserSession

from .schemas.Users import UserLogin, NewUser

from .services.users import (
    login, logout, create_user, setup_default_user, delete_expired_sessions,
    get_current_session, get_current_user,
)

from sqlalchemy.orm import Session

app = FastAPI(title="5e Digital Character Sheet")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- App Startup ---

@app.on_event("startup")
def on_startup():
    create_tables()
    with SessionLocal() as db:
        setup_default_user(db)
        delete_expired_sessions(db)

# --- Users and Login ---

@app.post("/api/create_user/", tags=["Users"])
def create_user_endpoint(new_user: NewUser, db: Session = Depends(get_db)):
    """Creates a new user using the provided credentials. Optionally logs the new user in by returning a session token."""

    user = create_user(new_user.username, new_user.password, db)
    response = {"username": user.username}
    if new_user.login_after:
        response["session_token"] = login(new_user.username, new_user.password, db)
    return response


@app.post("/api/login/", tags=["Users"])
def login_endpoint(user_login: UserLogin, db: Session = Depends(get_db)):
    """Given a username and password, validate the users credentials and return a session token."""
    
    return {"session_token": login(user_login.username, user_login.password, db)}


@app.get("/api/me/", tags=["Users"])
def me_endpoint(user: User = Depends(get_current_user)):
    """Returns the user that owns the session token given in the Authorization header."""

    return {"username": user.username}


@app.post("/api/logout/", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
def logout_endpoint(user_session: UserSession = Depends(get_current_session), db: Session = Depends(get_db)):
    """Ends the session given in the Authorization header."""

    logout(user_session, db)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

