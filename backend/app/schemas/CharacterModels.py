from pydantic import BaseModel, ConfigDict

from ..models.Enums import Ability, AttackType, CasterType, FeatCategory, SpellSchool


class ContentSchema(BaseModel):
    """Fields shared by every character component model (see ContentMixin)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    key: str
    name: str
    description: str
    source: str


class CharacterClassSchema(ContentSchema):
    hit_die: int
    primary_abilities: list
    saving_throws: list
    spellcasting_ability: Ability | None
    caster_type: CasterType
    prepares_spells: bool
    spell_list_id: int | None
    subclass_level: int
    multiclass_prerequisites: dict
    starting_equipment: list


class SubclassSchema(ContentSchema):
    class_id: int


class SpeciesSchema(ContentSchema):
    size: str
    speed: int
    creature_type: str


class BackgroundSchema(ContentSchema):
    ability_options: list
    feat_id: int | None
    skill_proficiencies: list
    tool_proficiency: str
    equipment: list


class FeatSchema(ContentSchema):
    category: FeatCategory
    prerequisites: dict
    repeatable: bool
    effects: list


class SpellSchema(ContentSchema):
    level: int
    school: SpellSchool
    casting_time: str
    ritual: bool
    range: str
    area: dict | None
    components: dict
    duration: str
    concentration: bool
    attack_type: AttackType | None
    save_ability: Ability | None
    damage: list
    higher_levels: str
    scaling: dict | None
