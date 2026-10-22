from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db.db import SessionLocal, create_tables, get_db

from .schemas.Users import UserLogin, NewUser

from .services.users import login, create_user, setup_default_user

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

@app.post("/api/create_user/")
def create_user_endpoint(new_user: NewUser, db: Session = Depends(get_db)):
    user = create_user(new_user.username, new_user.password, db)
    response = {"username": user.username}
    if new_user.login_after:
        response["session_token"] = login(new_user.username, new_user.password, db)
    return response


@app.post("/api/login/")
def login_endpoint(user_login: UserLogin, db: Session = Depends(get_db)):
    return {"session_token": login(user_login.username, user_login.password, db)}

