from typing import TYPE_CHECKING

from .ContentMixin import ContentMixin
from .Enums import Ability, CasterType
from .ModelBase import ModelBase

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .Progression import Progression
    from .SpellList import SpellList
    from .Subclass import Subclass


class CharacterClass(ContentMixin, ModelBase):
    """A class that a character can take, such as "Wizard" or "Barbarian". (BG3: ClassDescriptions)

    Holds only static facts about the class. What the class grants at each level lives in Progression.
    """
    __tablename__ = "character_class"
    __table_args__ = (
        CheckConstraint("hit_die IN (6, 8, 10, 12)", name="ck_character_class_hit_die"),
    )

    hit_die: Mapped[int] = mapped_column()
    primary_abilities: Mapped[list] = mapped_column(JSONB, default=list)        # List of Ability values
    saving_throws: Mapped[list] = mapped_column(JSONB, default=list)            # List of Ability values
    spellcasting_ability: Mapped[Ability | None] = mapped_column()
    caster_type: Mapped[CasterType] = mapped_column(default=CasterType.NONE)
    prepares_spells: Mapped[bool] = mapped_column(default=False)
    spell_list_id: Mapped[int | None] = mapped_column(ForeignKey("spell_list.id", ondelete="SET NULL"))
    subclass_level: Mapped[int] = mapped_column(default=3)
    multiclass_prerequisites: Mapped[dict] = mapped_column(JSONB, default=dict)  # e.g. {"strength": 13}
    starting_equipment: Mapped[list] = mapped_column(JSONB, default=list)

    # Relationships
    spell_list: Mapped["SpellList | None"] = relationship()
    subclasses: Mapped[list["Subclass"]] = relationship(back_populates="character_class", cascade="all, delete-orphan")
    progressions: Mapped[list["Progression"]] = relationship(
        back_populates="character_class", cascade="all, delete-orphan", order_by="Progression.level"
    )
