"""The character sheet document: the structure stored in Character.data."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Abilities(Strict):
    strength: int = Field(10, ge=1, le=30)
    dexterity: int = Field(10, ge=1, le=30)
    constitution: int = Field(10, ge=1, le=30)
    intelligence: int = Field(10, ge=1, le=30)
    wisdom: int = Field(10, ge=1, le=30)
    charisma: int = Field(10, ge=1, le=30)


class HitPoints(Strict):
    max: int = Field(10, ge=0, le=9999)
    current: int = Field(10, ge=0, le=9999)
    temp: int = Field(0, ge=0, le=9999)


class DeathSaves(Strict):
    successes: int = Field(0, ge=0, le=3)
    failures: int = Field(0, ge=0, le=3)


class Currency(Strict):
    cp: int = Field(0, ge=0)
    sp: int = Field(0, ge=0)
    ep: int = Field(0, ge=0)
    gp: int = Field(0, ge=0)
    pp: int = Field(0, ge=0)


class Item(Strict):
    name: str = Field(min_length=1, max_length=100)
    quantity: int = Field(1, ge=0, le=100_000)
    weight: float = Field(0, ge=0, le=100_000)  # per unit, in lb
    kind: Literal["gear", "weapon", "armor", "shield"] = "gear"
    armor_type: Literal["light", "medium", "heavy"] | None = None  # armor only
    base_ac: int | None = Field(None, ge=0, le=30)  # armor only
    ac_bonus: int = Field(0, ge=-10, le=10)  # shield (+2) or magic bonus
    equipped: bool = False
    description: str = Field("", max_length=1000)


class Resource(Strict):
    """A trackable pool such as Ki, Rage, Channel Divinity or Bardic Inspiration."""

    name: str = Field(min_length=1, max_length=100)
    maximum: int = Field(1, ge=0, le=999)
    used: int = Field(0, ge=0, le=999)
    recharge: Literal["short", "long", "none"] = "long"


class SlotLevel(Strict):
    maximum: int = Field(0, ge=0, le=99)
    used: int = Field(0, ge=0, le=99)


class Sheet(Strict):
    name: str = Field("Unnamed Adventurer", min_length=1, max_length=100)
    race: str = Field("", max_length=50)
    character_class: str = Field("", max_length=50)
    subclass: str = Field("", max_length=50)
    background: str = Field("", max_length=50)
    alignment: str = Field("", max_length=30)
    level: int = Field(1, ge=1, le=20)
    experience: int = Field(0, ge=0)
    inspiration: bool = False

    abilities: Abilities = Abilities()
    save_proficiencies: list[str] = []
    skill_proficiencies: list[str] = []
    skill_expertise: list[str] = []

    hp: HitPoints = HitPoints()
    hit_dice_used: int = Field(0, ge=0, le=20)
    death_saves: DeathSaves = DeathSaves()

    inventory: list[Item] = []
    currency: Currency = Currency()
    resources: list[Resource] = []
    spell_slots: dict[int, SlotLevel] = {}
    conditions: list[str] = []
    notes: str = Field("", max_length=20_000)

    @field_validator("save_proficiencies", "skill_proficiencies", "skill_expertise", "conditions")
    @classmethod
    def _normalise(cls, v: list[str]) -> list[str]:
        out: list[str] = []
        for s in v:
            s = s.strip().lower().replace(" ", "_")
            if s and s not in out:
                out.append(s)
        return out

    @field_validator("spell_slots")
    @classmethod
    def _slot_levels(cls, v: dict[int, SlotLevel]) -> dict[int, SlotLevel]:
        if any(not 1 <= k <= 9 for k in v):
            raise ValueError("spell slot levels must be between 1 and 9")
        return v


class LayoutItem(Strict):
    """Position/size of one UI panel. The backend only stores and sanity-checks this."""

    id: str = Field(min_length=1, max_length=50)
    order: int = Field(ge=0, le=1000)
    width: int | None = Field(None, ge=1, le=100)
    height: int | None = Field(None, ge=1, le=100)
    visible: bool = True
