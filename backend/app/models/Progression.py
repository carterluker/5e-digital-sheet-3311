from typing import TYPE_CHECKING

from .ModelBase import ModelBase

from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .CharacterClass import CharacterClass
    from .Feature import Feature
    from .ProgressionChoice import ProgressionChoice
    from .Species import Species
    from .Subclass import Subclass


class Progression(ModelBase):
    """What a CharacterClass, Subclass, or Species grants at a given level. (BG3: Progressions)

    Exactly one of class_id, subclass_id, or species_id is set. Automatic grants are stored in
    `effects` (BG3: Boosts) and `features` (BG3: PassivesAdded); player choices are ProgressionChoice
    rows (BG3: Selectors).
    """
    __tablename__ = "progression"
    __table_args__ = (
        CheckConstraint("num_nonnulls(class_id, subclass_id, species_id) = 1", name="ck_progression_one_owner"),
        CheckConstraint("level BETWEEN 1 AND 20", name="ck_progression_level"),
        UniqueConstraint("class_id", "level"),
        UniqueConstraint("subclass_id", "level"),
        UniqueConstraint("species_id", "level"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    class_id: Mapped[int | None] = mapped_column(ForeignKey("character_class.id", ondelete="CASCADE"))
    subclass_id: Mapped[int | None] = mapped_column(ForeignKey("subclass.id", ondelete="CASCADE"))
    species_id: Mapped[int | None] = mapped_column(ForeignKey("species.id", ondelete="CASCADE"))
    level: Mapped[int] = mapped_column()

    effects: Mapped[list] = mapped_column(JSONB, default=list)  # Automatic grants: proficiencies, resources, ability bonuses, etc.
    allow_improvement: Mapped[bool] = mapped_column(default=False)  # Ability Score Improvement or Feat gained at this level
    grants_subclass: Mapped[bool] = mapped_column(default=False)    # Subclass chosen at this level

    # Relationships
    character_class: Mapped["CharacterClass | None"] = relationship(back_populates="progressions")
    subclass: Mapped["Subclass | None"] = relationship(back_populates="progressions")
    species: Mapped["Species | None"] = relationship(back_populates="progressions")
    features: Mapped[list["Feature"]] = relationship(secondary="progression_feature")
    choices: Mapped[list["ProgressionChoice"]] = relationship(back_populates="progression", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        owner = f"class_id={self.class_id}" if self.class_id is not None \
            else f"subclass_id={self.subclass_id}" if self.subclass_id is not None \
            else f"species_id={self.species_id}"
        return f"Progression({owner}, level={self.level})"
