from typing import TYPE_CHECKING

from .ContentMixin import ContentMixin
from .ModelBase import ModelBase

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .Resource import Resource


class Feature(ContentMixin, ModelBase):
    """A named feature, such as "Rage", "Darkvision", or "Fighting Style: Archery". (BG3: Passives)"""
    __tablename__ = "feature"

    effects: Mapped[list] = mapped_column(JSONB, default=list)
    resource_id: Mapped[int | None] = mapped_column(ForeignKey("resource.id", ondelete="SET NULL"))  # Resource this feature uses

    # Relationships
    resource: Mapped["Resource | None"] = relationship()
