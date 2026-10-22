from typing import TYPE_CHECKING

from .ContentMixin import ContentMixin
from .ModelBase import ModelBase

from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    from .Spell import Spell


class SpellList(ContentMixin, ModelBase):
    """A reusable set of Spells, such as "Wizard Spells" or "Wizard Cantrips". (BG3: SpellLists)"""
    __tablename__ = "spell_list"

    # Relationships
    spells: Mapped[list["Spell"]] = relationship(secondary="spell_list_entry")
