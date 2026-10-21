# TODO: Trim uneeded imports

from datetime import datetime

from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Class(DeclarativeBase):
    __tablename__ = "class"
    id: Mapped[int] = mapped_column(primary_key=True)
    def __repr__(self) -> str:
        return "TODO"