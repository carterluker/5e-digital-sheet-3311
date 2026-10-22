from typing import TYPE_CHECKING

from .Enums import FeatSource
from .ModelBase import ModelBase

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .Character import Character
    from .Feat import Feat


class CharacterFeat(ModelBase):
    """A Feat a Character has taken, and where it came from. Has its own id since some feats are repeatable."""
    __tablename__ = "character_feat"

    id: Mapped[int] = mapped_column(primary_key=True)
    character_id: Mapped[int] = mapped_column(ForeignKey("character.id", ondelete="CASCADE"), index=True)
    feat_id: Mapped[int] = mapped_column(ForeignKey("feat.id"))
    source: Mapped[FeatSource] = mapped_column()
    level_taken: Mapped[int] = mapped_column(default=1)

    # Relationships
    character: Mapped["Character"] = relationship(back_populates="feats")
    feat: Mapped["Feat"] = relationship()

    def __repr__(self) -> str:
        return f"CharacterFeat(character_id={self.character_id}, feat_id={self.feat_id}, source={self.source})"
