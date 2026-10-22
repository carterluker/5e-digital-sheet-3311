from .ContentMixin import ContentMixin
from .Enums import Ability, AttackType, SpellSchool
from .ModelBase import ModelBase

from sqlalchemy import CheckConstraint, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class Spell(ContentMixin, ModelBase):
    """A spell, such as "Fire Bolt" or "Fireball". (BG3: Spell stats)"""
    __tablename__ = "spell"
    __table_args__ = (
        CheckConstraint("level BETWEEN 0 AND 9", name="ck_spell_level"),
    )

    level: Mapped[int] = mapped_column(index=True)  # 0 = Cantrip
    school: Mapped[SpellSchool] = mapped_column()
    casting_time: Mapped[str] = mapped_column(String(100))
    ritual: Mapped[bool] = mapped_column(default=False)
    range: Mapped[str] = mapped_column(String(100))
    area: Mapped[dict | None] = mapped_column(JSONB)          # e.g. {"shape": "sphere", "size": 20}
    components: Mapped[dict] = mapped_column(JSONB, default=dict)  # {"verbal": bool, "somatic": bool, "material": str | None}
    duration: Mapped[str] = mapped_column(String(100))
    concentration: Mapped[bool] = mapped_column(default=False)

    attack_type: Mapped[AttackType | None] = mapped_column()  # BG3: SpellRoll Attack()
    save_ability: Mapped[Ability | None] = mapped_column()    # BG3: SpellRoll SavingThrow()
    damage: Mapped[list] = mapped_column(JSONB, default=list)  # e.g. [{"dice": "8d6", "type": "fire"}]

    higher_levels: Mapped[str] = mapped_column(Text, default="")
    scaling: Mapped[dict | None] = mapped_column(JSONB)       # Structured upcast/cantrip scaling, if any
