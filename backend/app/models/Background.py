from typing import TYPE_CHECKING

from .ContentMixin import ContentMixin
from .ModelBase import ModelBase

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .Feat import Feat


class Background(ContentMixin, ModelBase):
    """A character background, such as "Sage" or "Soldier"."""
    __tablename__ = "background"

    ability_options: Mapped[list] = mapped_column(JSONB, default=list)      # The 3 Ability values eligible for +2/+1 or +1/+1/+1
    feat_id: Mapped[int | None] = mapped_column(ForeignKey("feat.id", ondelete="SET NULL"))  # Origin feat
    skill_proficiencies: Mapped[list] = mapped_column(JSONB, default=list)
    tool_proficiency: Mapped[str] = mapped_column(String(100), default="")
    equipment: Mapped[list] = mapped_column(JSONB, default=list)

    # Relationships
    feat: Mapped["Feat | None"] = relationship()
