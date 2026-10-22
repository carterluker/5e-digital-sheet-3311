from typing import TYPE_CHECKING

from .ContentMixin import ContentMixin
from .ModelBase import ModelBase

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .CharacterClass import CharacterClass
    from .Progression import Progression


class Subclass(ContentMixin, ModelBase):
    """A subclass that provides features in addition to those of its parent CharacterClass. (BG3: ClassDescriptions with ParentUUID)"""
    __tablename__ = "subclass"

    class_id: Mapped[int] = mapped_column(ForeignKey("character_class.id", ondelete="CASCADE"), index=True)

    # Relationships
    character_class: Mapped["CharacterClass"] = relationship(back_populates="subclasses")
    progressions: Mapped[list["Progression"]] = relationship(
        back_populates="subclass", cascade="all, delete-orphan", order_by="Progression.level"
    )
