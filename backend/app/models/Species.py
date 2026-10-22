from typing import TYPE_CHECKING

from .ContentMixin import ContentMixin
from .ModelBase import ModelBase

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .Progression import Progression


class Species(ContentMixin, ModelBase):
    """A character species, such as "Elf" or "Dwarf". Traits are granted through its Progression. (BG3: Races)"""
    __tablename__ = "species"

    size: Mapped[str] = mapped_column(String(50))  # e.g. "Medium", or "Small or Medium"
    speed: Mapped[int] = mapped_column(default=30)
    creature_type: Mapped[str] = mapped_column(String(50), default="Humanoid")

    # Relationships
    progressions: Mapped[list["Progression"]] = relationship(
        back_populates="species", cascade="all, delete-orphan", order_by="Progression.level"
    )
