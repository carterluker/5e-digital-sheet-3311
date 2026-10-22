# TODO: Trim uneeded imports

from datetime import datetime

from .ModelBase import ModelBase

from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

class CharacterClass(ModelBase):
    __tablename__ = "character_class"
    id: Mapped[int] = mapped_column(primary_key=True)
    def __repr__(self) -> str:
        return "TODO"