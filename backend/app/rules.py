"""5e (SRD) rules data, derived statistics and sheet validation."""
from dataclasses import dataclass
from typing import Literal

from pydantic import BaseModel

from .sheet import Sheet

ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]

SKILLS = {
    "acrobatics": "dexterity",
    "animal_handling": "wisdom",
    "arcana": "intelligence",
    "athletics": "strength",
    "deception": "charisma",
    "history": "intelligence",
    "insight": "wisdom",
    "intimidation": "charisma",
    "investigation": "intelligence",
    "medicine": "wisdom",
    "nature": "intelligence",
    "perception": "wisdom",
    "performance": "charisma",
    "persuasion": "charisma",
    "religion": "intelligence",
    "sleight_of_hand": "dexterity",
    "stealth": "dexterity",
    "survival": "wisdom",
}


@dataclass(frozen=True)
class ClassInfo:
    hit_die: int
    saves: tuple[str, str]
    caster: Literal["full", "half", "pact"] | None = None
    spell_ability: str | None = None


CLASSES = {
    "barbarian": ClassInfo(12, ("strength", "constitution")),
    "bard": ClassInfo(8, ("dexterity", "charisma"), "full", "charisma"),
    "cleric": ClassInfo(8, ("wisdom", "charisma"), "full", "wisdom"),
    "druid": ClassInfo(8, ("intelligence", "wisdom"), "full", "wisdom"),
    "fighter": ClassInfo(10, ("strength", "constitution")),
    "monk": ClassInfo(8, ("strength", "dexterity")),
    "paladin": ClassInfo(10, ("wisdom", "charisma"), "half", "charisma"),
    "ranger": ClassInfo(10, ("strength", "dexterity"), "half", "wisdom"),
    "rogue": ClassInfo(8, ("dexterity", "intelligence")),
    "sorcerer": ClassInfo(6, ("constitution", "charisma"), "full", "charisma"),
    "warlock": ClassInfo(8, ("wisdom", "charisma"), "pact", "charisma"),
    "wizard": ClassInfo(6, ("intelligence", "wisdom"), "full", "intelligence"),
}

RACES = {
    "dragonborn", "dwarf", "elf", "gnome", "half-elf", "half-orc", "halfling", "human", "tiefling",
}

# Spell slots per spell level (1st..9th) for a full caster, indexed by caster level 1..20.
FULL_CASTER_SLOTS = [
    [2], [3], [4, 2], [4, 3], [4, 3, 2], [4, 3, 3], [4, 3, 3, 1], [4, 3, 3, 2], [4, 3, 3, 3, 1],
    [4, 3, 3, 3, 2], [4, 3, 3, 3, 2, 1], [4, 3, 3, 3, 2, 1], [4, 3, 3, 3, 2, 1, 1],
    [4, 3, 3, 3, 2, 1, 1], [4, 3, 3, 3, 2, 1, 1, 1], [4, 3, 3, 3, 2, 1, 1, 1],
    [4, 3, 3, 3, 2, 1, 1, 1, 1], [4, 3, 3, 3, 3, 1, 1, 1, 1], [4, 3, 3, 3, 3, 2, 1, 1, 1],
    [4, 3, 3, 3, 3, 2, 2, 1, 1],
]

ARMOR_DEX_CAP = {"light": None, "medium": 2, "heavy": 0}


def modifier(score: int) -> int:
    return (score - 10) // 2


def proficiency_bonus(level: int) -> int:
    return 2 + (level - 1) // 4


def class_info(sheet: Sheet) -> ClassInfo | None:
    return CLASSES.get(sheet.character_class.strip().lower())


def max_slots(info: ClassInfo, level: int) -> list[int] | None:
    """Slot ceiling for full/half casters, else None (unknown/subclass dependent)."""
    if info.caster == "full":
        return FULL_CASTER_SLOTS[level - 1]
    if info.caster == "half":
        return FULL_CASTER_SLOTS[(level + 1) // 2 - 1] if level >= 2 else []
    return None


# ---------------------------------------------------------------- derived stats

def armor_class(sheet: Sheet) -> int:
    mods = {a: modifier(getattr(sheet.abilities, a)) for a in ABILITIES}
    equipped = [i for i in sheet.inventory if i.equipped and i.quantity > 0]
    armor = next((i for i in equipped if i.kind == "armor" and i.base_ac is not None), None)
    has_shield = any(i.kind == "shield" for i in equipped)
    bonus = sum(i.ac_bonus for i in equipped)  # shield +2 and magic bonuses

    if armor:
        cap = ARMOR_DEX_CAP[armor.armor_type or "light"]
        dex = mods["dexterity"] if cap is None else min(mods["dexterity"], cap)
        base = armor.base_ac + dex
    else:
        base = 10 + mods["dexterity"]
        cls = sheet.character_class.strip().lower()
        if cls == "barbarian":
            base += mods["constitution"]
        elif cls == "monk" and not has_shield:
            base += mods["wisdom"]
    return base + bonus


class Derived(BaseModel):
    proficiency_bonus: int
    ability_modifiers: dict[str, int]
    saving_throws: dict[str, int]
    skills: dict[str, int]
    initiative: int
    armor_class: int
    passive_perception: int
    hit_die: int | None
    hit_dice_total: int
    hit_dice_remaining: int
    spell_save_dc: int | None
    spell_attack_bonus: int | None
    total_weight: float
    carrying_capacity: int
    encumbered: bool


def derive(sheet: Sheet) -> Derived:
    prof = proficiency_bonus(sheet.level)
    mods = {a: modifier(getattr(sheet.abilities, a)) for a in ABILITIES}
    saves = {a: mods[a] + (prof if a in sheet.save_proficiencies else 0) for a in ABILITIES}
    skills = {}
    for skill, ability in SKILLS.items():
        mult = 2 if skill in sheet.skill_expertise else 1 if skill in sheet.skill_proficiencies else 0
        skills[skill] = mods[ability] + prof * mult
    info = class_info(sheet)
    spell_mod = mods[info.spell_ability] if info and info.spell_ability else None
    weight = sum(i.weight * i.quantity for i in sheet.inventory)
    capacity = sheet.abilities.strength * 15
    return Derived(
        proficiency_bonus=prof,
        ability_modifiers=mods,
        saving_throws=saves,
        skills=skills,
        initiative=mods["dexterity"],
        armor_class=armor_class(sheet),
        passive_perception=10 + skills["perception"],
        hit_die=info.hit_die if info else None,
        hit_dice_total=sheet.level,
        hit_dice_remaining=max(sheet.level - sheet.hit_dice_used, 0),
        spell_save_dc=8 + prof + spell_mod if spell_mod is not None else None,
        spell_attack_bonus=prof + spell_mod if spell_mod is not None else None,
        total_weight=round(weight, 2),
        carrying_capacity=capacity,
        encumbered=weight > capacity,
    )


# ------------------------------------------------------------------- validation

class Issue(BaseModel):
    severity: Literal["error", "warning"]
    path: str
    message: str


def validate(sheet: Sheet) -> list[Issue]:
    """Check a structurally valid sheet against 5e rules.

    Errors are things the rules forbid outright; warnings are things that are
    unusual but possible (homebrew, feats, magic items, multiclassing).
    """
    issues: list[Issue] = []

    def err(path: str, msg: str):
        issues.append(Issue(severity="error", path=path, message=msg))

    def warn(path: str, msg: str):
        issues.append(Issue(severity="warning", path=path, message=msg))

    info = class_info(sheet)
    if sheet.character_class and info is None:
        warn("character_class", f"'{sheet.character_class}' is not an SRD class (homebrew?)")
    if sheet.race and sheet.race.strip().lower() not in RACES:
        warn("race", f"'{sheet.race}' is not an SRD race (homebrew?)")

    for a in ABILITIES:
        if getattr(sheet.abilities, a) > 20:
            warn(f"abilities.{a}", "Ability scores above 20 are normally only reachable via magic or epic boons")

    for i, s in enumerate(sheet.save_proficiencies):
        if s not in ABILITIES:
            err(f"save_proficiencies[{i}]", f"'{s}' is not an ability")
    if info and set(sheet.save_proficiencies) != set(info.saves):
        warn("save_proficiencies", f"A {sheet.character_class} is normally proficient in {' and '.join(info.saves)} saves")

    for i, s in enumerate(sheet.skill_proficiencies):
        if s not in SKILLS:
            err(f"skill_proficiencies[{i}]", f"'{s}' is not a skill")
    for i, s in enumerate(sheet.skill_expertise):
        if s not in SKILLS:
            err(f"skill_expertise[{i}]", f"'{s}' is not a skill")
        elif s not in sheet.skill_proficiencies:
            err(f"skill_expertise[{i}]", f"Expertise in {s} requires proficiency in it")

    hp = sheet.hp
    if hp.current > hp.max:
        err("hp.current", "Current HP cannot exceed maximum HP")
    if info:
        con = modifier(sheet.abilities.constitution)
        ceiling = sheet.level * max(info.hit_die + con, 1)
        if hp.max > ceiling:
            warn("hp.max", f"Max HP {hp.max} exceeds the level-{sheet.level} {sheet.character_class} maximum of {ceiling} (feats/items may explain this)")
    if sheet.hit_dice_used > sheet.level:
        err("hit_dice_used", "Cannot have spent more hit dice than character level")
    if hp.current > 0 and (sheet.death_saves.successes or sheet.death_saves.failures):
        warn("death_saves", "Death saves are only tracked while at 0 HP")

    equipped_armor = [i for i in sheet.inventory if i.equipped and i.kind == "armor"]
    equipped_shields = [i for i in sheet.inventory if i.equipped and i.kind == "shield"]
    if len(equipped_armor) > 1:
        err("inventory", "Only one suit of armor can be worn at a time")
    if len(equipped_shields) > 1:
        err("inventory", "Only one shield can be carried at a time")
    for i, item in enumerate(sheet.inventory):
        if item.kind == "armor" and (item.base_ac is None or item.armor_type is None):
            err(f"inventory[{i}]", "Armor needs base_ac and armor_type")
    for armor in equipped_armor:
        if armor.armor_type == "heavy" and sheet.abilities.strength < 13:
            warn("inventory", f"Heavy armor ({armor.name}) usually requires Strength 13-15; speed may be reduced")

    for i, r in enumerate(sheet.resources):
        if r.used > r.maximum:
            err(f"resources[{i}]", f"{r.name}: used ({r.used}) exceeds maximum ({r.maximum})")

    ceiling_slots = max_slots(info, sheet.level) if info else None
    for lvl, slot in sheet.spell_slots.items():
        if slot.used > slot.maximum:
            err(f"spell_slots.{lvl}", f"Level {lvl}: used ({slot.used}) exceeds maximum ({slot.maximum})")
        if ceiling_slots is not None:
            allowed = ceiling_slots[lvl - 1] if lvl <= len(ceiling_slots) else 0
            if slot.maximum > allowed:
                err(f"spell_slots.{lvl}", f"A level-{sheet.level} {sheet.character_class} has at most {allowed} level-{lvl} slots")

    return issues
