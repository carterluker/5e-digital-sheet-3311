from .ModelBase import ModelBase

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column


class FeatureListEntry(ModelBase):
    """Association: a Feature belonging to a FeatureList."""
    __tablename__ = "feature_list_entry"

    feature_list_id: Mapped[int] = mapped_column(ForeignKey("feature_list.id", ondelete="CASCADE"), primary_key=True)
    feature_id: Mapped[int] = mapped_column(ForeignKey("feature.id", ondelete="CASCADE"), primary_key=True)

    def __repr__(self) -> str:
        return f"FeatureListEntry(feature_list_id={self.feature_list_id}, feature_id={self.feature_id})"
