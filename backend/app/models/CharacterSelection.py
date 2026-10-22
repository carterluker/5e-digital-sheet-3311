from typing import TYPE_CHECKING

from .ModelBase import ModelBase

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .Character import Character
    from .ProgressionChoice import ProgressionChoice


class CharacterSelection(ModelBase):
    """What a Character picked for one ProgressionChoice, e.g. ["athletics", "perception"]."""
    __tablename__ = "character_selection"

    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("character.id", ondelete="CASCADE"), index=True)
    choice_id: Mapped[int] = mapped_column(ForeignKey("progression_choice.id"))
    level_taken: Mapped[int] = mapped_column()
    value: Mapped[list] = mapped_column(JSONB, default=list)  # Keys of the chosen spells, features, skills, etc.

    # Relationships
    character: Mapped["Character"] = relationship(back_populates="selections")
    choice: Mapped["ProgressionChoice"] = relationship()

    def __repr__(self) -> str:
        return f"CharacterSelection(character_id={self.character_id}, choice_id={self.choice_id}, value={self.value!r})"
