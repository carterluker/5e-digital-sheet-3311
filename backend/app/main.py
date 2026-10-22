from argon2 import PasswordHasher

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db.db import create_tables, get_db

from .models.User import User

from .services.users import login, create_user

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

# --- Users and Login ---

@app.get("/api/create_user/{username},{password},{login}")
async def create_user(username: str, password: str, login: bool, db: Session = Depends(get_db)):
    create_user(username, password)
    if login:
        


@app.get("/api/login/{username},{password}")
async def login(username: str, password: str):
    session_token = login(username, password)
    return 

