from typing import TYPE_CHECKING

from .ContentMixin import ContentMixin
from .Enums import FeatCategory
from .ModelBase import ModelBase

from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .ProgressionChoice import ProgressionChoice


class Feat(ContentMixin, ModelBase):
    """An optional feature taken from a Background or an Ability Score Improvement, such as "Alert"."""
    __tablename__ = "feat"

    category: Mapped[FeatCategory] = mapped_column()
    prerequisites: Mapped[dict] = mapped_column(JSONB, default=dict)  # e.g. {"level": 4, "abilities": {"strength": 13}}
    repeatable: Mapped[bool] = mapped_column(default=False)
    effects: Mapped[list] = mapped_column(JSONB, default=list)

    # Relationships
    choices: Mapped[list["ProgressionChoice"]] = relationship(back_populates="feat", cascade="all, delete-orphan")
