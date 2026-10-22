from typing import TYPE_CHECKING

from .Enums import ChoiceType
from .ModelBase import ModelBase

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from .Feat import Feat
    from .FeatureList import FeatureList
    from .Progression import Progression
    from .SpellList import SpellList


class ProgressionChoice(ModelBase):
    """A choice the player makes, e.g. "Choose a Fighting Style". (BG3: Selectors + ProgressionDescriptions)

    Belongs to exactly one of a Progression or a Feat. Options come from `spell_list` (SPELL),
    `feature_list` (FEATURE), or the fixed `options` list (SKILL, EXPERTISE, ABILITY).
    """
    __tablename__ = "progression_choice"
    __table_args__ = (
        CheckConstraint("num_nonnulls(progression_id, feat_id) = 1", name="ck_progression_choice_one_owner"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    progression_id: Mapped[int | None] = mapped_column(ForeignKey("progression.id", ondelete="CASCADE"), index=True)
    feat_id: Mapped[int | None] = mapped_column(ForeignKey("feat.id", ondelete="CASCADE"), index=True)

    choice_type: Mapped[ChoiceType] = mapped_column()
    spell_list_id: Mapped[int | None] = mapped_column(ForeignKey("spell_list.id"))
    feature_list_id: Mapped[int | None] = mapped_column(ForeignKey("feature_list.id"))
    options: Mapped[list | None] = mapped_column(JSONB)  # e.g. skill keys, for choices not drawn from a list

    count: Mapped[int] = mapped_column(default=1)
    replace_count: Mapped[int] = mapped_column(default=0)  # Previously chosen options that may be swapped out
    label: Mapped[str] = mapped_column(String(255))         # Player-facing, e.g. "Choose a Fighting Style"
    selector_key: Mapped[str] = mapped_column(String(100))  # Stable identifier, e.g. "fighting_style"

    # Relationships
    progression: Mapped["Progression | None"] = relationship(back_populates="choices")
    feat: Mapped["Feat | None"] = relationship(back_populates="choices")
    spell_list: Mapped["SpellList | None"] = relationship()
    feature_list: Mapped["FeatureList | None"] = relationship()

    def __repr__(self) -> str:
        return f"ProgressionChoice(selector_key={self.selector_key!r}, choice_type={self.choice_type}, count={self.count})"
