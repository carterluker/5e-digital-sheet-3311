from typing import TYPE_CHECKING

from .ModelBase import ModelBase

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .Character import Character
    from .Resource import Resource


class CharacterResourceState(ModelBase):
    """How much of a Resource a Character has used. The maximum is always computed, never stored."""
    __tablename__ = "character_resource_state"

    character_id: Mapped[int] = mapped_column(ForeignKey("character.id", ondelete="CASCADE"), primary_key=True)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resource.id", ondelete="CASCADE"), primary_key=True)
    used: Mapped[int] = mapped_column(default=0)

    # Relationships
    character: Mapped["Character"] = relationship(back_populates="resource_states")
    resource: Mapped["Resource"] = relationship()

    def __repr__(self) -> str:
        return f"CharacterResourceState(character_id={self.character_id}, resource_id={self.resource_id}, used={self.used})"
