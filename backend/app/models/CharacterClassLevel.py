from typing import TYPE_CHECKING

from .ModelBase import ModelBase

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .Character import Character
    from .CharacterClass import CharacterClass
    from .Subclass import Subclass


class CharacterClassLevel(ModelBase):
    """Levels a Character has taken in one CharacterClass (and its Subclass, once chosen). Multiple rows = multiclassing."""
    __tablename__ = "character_class_level"
    __table_args__ = (
        UniqueConstraint("character_id", "class_id"),
        CheckConstraint("levels BETWEEN 1 AND 20", name="ck_character_class_level_levels"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("character.id", ondelete="CASCADE"), index=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("character_class.id"))
    subclass_id: Mapped[int | None] = mapped_column(ForeignKey("subclass.id"))
    levels: Mapped[int] = mapped_column(default=1)

    # Relationships
    character: Mapped["Character"] = relationship(back_populates="class_levels")
    character_class: Mapped["CharacterClass"] = relationship()
    subclass: Mapped["Subclass | None"] = relationship()

    def __repr__(self) -> str:
        return f"CharacterClassLevel(character_id={self.character_id}, class_id={self.class_id}, levels={self.levels})"
