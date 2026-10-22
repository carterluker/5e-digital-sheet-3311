from typing import TYPE_CHECKING

from .ContentMixin import ContentMixin
from .ModelBase import ModelBase

from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    from .Feature import Feature


class FeatureList(ContentMixin, ModelBase):
    """A reusable set of Features, such as "Fighting Styles" or "Metamagic Options". (BG3: PassiveLists)"""
    __tablename__ = "feature_list"

    # Relationships
    features: Mapped[list["Feature"]] = relationship(secondary="feature_list_entry")
