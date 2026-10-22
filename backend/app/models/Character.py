from datetime import datetime, timezone
from typing import TYPE_CHECKING

from .ModelBase import ModelBase

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .User import User

if TYPE_CHECKING:
    from .Background import Background
    from .CharacterClassLevel import CharacterClassLevel
    from .CharacterFeat import CharacterFeat
    from .CharacterResourceState import CharacterResourceState
    from .CharacterSelection import CharacterSelection
    from .Species import Species


def _now() -> datetime:
    return datetime.now(timezone.utc)


class Character(ModelBase):
    """A user's character. Only base values and player choices are stored; modifiers, proficiency bonus,
    saving throws, skill bonuses, etc. are always computed from the character's components."""

    __tablename__ = "character"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(255))

    species_id: Mapped[int | None] = mapped_column(ForeignKey("species.id", ondelete="SET NULL"))
    background_id: Mapped[int | None] = mapped_column(ForeignKey("background.id", ondelete="SET NULL"))
    alignment: Mapped[str | None] = mapped_column(String(50))

    # Base ability scores, before background, species, feat, etc. bonuses
    strength: Mapped[int] = mapped_column()
    dexterity: Mapped[int] = mapped_column()
    constitution: Mapped[int] = mapped_column()
    intelligence: Mapped[int] = mapped_column()
    wisdom: Mapped[int] = mapped_column()
    charisma: Mapped[int] = mapped_column()
    background_ability_bonuses: Mapped[dict] = mapped_column(JSONB, default=dict)  # e.g. {"strength": 2, "constitution": 1}

    experience: Mapped[int] = mapped_column(default=0)
    current_hp: Mapped[int] = mapped_column(default=0)
    temp_hp: Mapped[int] = mapped_column(default=0)
    hit_dice_spent: Mapped[int] = mapped_column(default=0)
    heroic_inspiration: Mapped[bool] = mapped_column(default=False)

    created_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now, onupdate=_now)

    # Relationships
    user: Mapped[User] = relationship()
    species: Mapped["Species | None"] = relationship()
    background: Mapped["Background | None"] = relationship()
    class_levels: Mapped[list["CharacterClassLevel"]] = relationship(back_populates="character", cascade="all, delete-orphan")
    selections: Mapped[list["CharacterSelection"]] = relationship(back_populates="character", cascade="all, delete-orphan")
    feats: Mapped[list["CharacterFeat"]] = relationship(back_populates="character", cascade="all, delete-orphan")
    resource_states: Mapped[list["CharacterResourceState"]] = relationship(back_populates="character", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Character(id={self.id}, name={self.name!r})"
