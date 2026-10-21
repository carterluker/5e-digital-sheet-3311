# TODO: Trim uneeded imports

from datetime import datetime

from ModelBase import ModelBase

from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class User(ModelBase):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(30), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    
    def __repr__(self) -> str:
        return "TODO"