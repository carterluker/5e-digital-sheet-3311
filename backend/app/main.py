from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from . import models  # noqa: F401  (registers tables on Base.metadata)
from .config import settings
from .db import Base, engine, get_db
from .routers import auth, characters


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Demo only: create tables on startup. A real deployment would use migrations (Alembic).
    Base.metadata.create_all(engine)
    yield


app = FastAPI(title="5e Digital Character Sheet", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(characters.router)


@app.get("/api/health")
def health(db: Session = Depends(get_db)) -> dict:
    db.execute(text("SELECT 1"))
    return {"status": "ok", "db": True}
