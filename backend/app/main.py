from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db.db import create_tables, get_db

from .models.User import User

from sqlalchemy import select
from sqlalchemy.exc import OperationalError, SQLAlchemyError
from sqlalchemy.orm import Session

app = FastAPI(title="5e Digital Character Sheet")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    try:
        create_tables()
    except OperationalError:
        # Database is down or timed out: 503
        raise TimeoutError("Database connection timed out. Could not create/validate database tables.")



@app.get("/api/login/{username},{password}")
async def login(username: str, password: str, db: Session = Depends(get_db)) -> str:

    # Get User
    try:
        user_result = db.execute(select(User).where(User.username == username))
    except OperationalError:
        # Database is down or timed out: 503
        raise HTTPException(
            status_code=503,
            detail="The backend database is unavailable."
        )
    except SQLAlchemyError:
        # Misc SQLAlchemy error: 500
        return

    if len(user_result) <= 0:
        # User does not exist under provided username.
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    if len(user_result) >= 2:
        # Something has gone horribly wrong. Usernames must be unique.
        raise HTTPException(
            status_code=500,
            detail="More than one user exists with this username."
        )

    