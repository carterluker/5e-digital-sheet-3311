from .ContentMixin import ContentMixin
from .Enums import Recharge
from .ModelBase import ModelBase

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class Resource(ContentMixin, ModelBase):
    """A limited-use resource, such as "Rage" or "Spell Slot (Level 1)". (BG3: ActionResources)"""
    __tablename__ = "resource"

    recharge: Mapped[Recharge] = mapped_column(default=Recharge.LONG_REST)
    max_formula: Mapped[str | None] = mapped_column(String(100))  # e.g. "proficiency_bonus"; None when set by a Progression's effects
