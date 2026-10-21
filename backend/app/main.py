from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings

from .db.db import create_db_and_tables, get_db

app = FastAPI(title="5e Digital Character Sheet")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/api/login/{username},{password}")
async def login(username: str, password: str) -> str:
    db = get_db()
    try:
        db.execute()
    except:
        pass