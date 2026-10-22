from .ModelBase import ModelBase

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class SpellListEntry(ModelBase):
    """Association: a Spell belonging to a SpellList."""
    __tablename__ = "spell_list_entry"

    spell_list_id: Mapped[int] = mapped_column(ForeignKey("spell_list.id", ondelete="CASCADE"), primary_key=True)
    spell_id: Mapped[int] = mapped_column(ForeignKey("spell.id", ondelete="CASCADE"), primary_key=True)

    def __repr__(self) -> str:
        return f"SpellListEntry(spell_list_id={self.spell_list_id}, spell_id={self.spell_id})"
