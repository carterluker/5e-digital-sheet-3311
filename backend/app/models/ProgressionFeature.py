from .ModelBase import ModelBase

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class ProgressionFeature(ModelBase):
    """Association: a Feature granted automatically by a Progression. (BG3: PassivesAdded)"""
    __tablename__ = "progression_feature"

    progression_id: Mapped[int] = mapped_column(ForeignKey("progression.id", ondelete="CASCADE"), primary_key=True)
    feature_id: Mapped[int] = mapped_column(ForeignKey("feature.id", ondelete="CASCADE"), primary_key=True)

    def __repr__(self) -> str:
        return f"ProgressionFeature(progression_id={self.progression_id}, feature_id={self.feature_id})"
