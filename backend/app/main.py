from argon2 import PasswordHasher

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db.db import SessionLocal, create_tables, get_db

from .models.User import User

from .services.users import login, create_user, setup_default_user

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
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

# --- Users and Login ---

@app.get("/api/create_user/{username},{password},{login_after}")
def create_user_endpoint(username: str, password: str, login_after: bool, db: Session = Depends(get_db)):
    user = create_user(username, password, db)
    response = {"username": user.username}
    if login_after:
        response["session_token"] = login(username, password, db)
    return response


@app.get("/api/login/{username},{password}")
def login_endpoint(username: str, password: str, db: Session = Depends(get_db)):
    return {"session_token": login(username, password, db)}

