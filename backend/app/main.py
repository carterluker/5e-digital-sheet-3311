from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .db.db import create_tables, get_db

from .models.User import User

from sqlalchemy import select
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
    create_tables()


@app.get("/api/login/{username},{password}")
async def login(username: str, password: str, db: Session = Depends(get_db)) -> str:
    #try:
    user = db.execute(select(User).where(User.username == username))
    #except:
    pass