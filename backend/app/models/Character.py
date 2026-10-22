from .ModelBase import ModelBase

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from .User import User

class Character(ModelBase):

    __tablename__ = "character"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))

    strength: Mapped[int] = mapped_column()
    dexterity: Mapped[int] = mapped_column()
    constitution: Mapped[int] = mapped_column()
    intelligence: Mapped[int] = mapped_column()
    wisdom: Mapped[int] = mapped_column()
    charisma: Mapped[int] = mapped_column()

    selected_skills: Mapped[list] = mapped_column(JSONB)

    # Relationships
    user: Mapped[User] = relationship()




    def __repr__(self) -> str:
        return "TODO"
