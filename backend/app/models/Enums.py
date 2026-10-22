import enum


class Ability(enum.Enum):
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"


class CasterType(enum.Enum):
    """Determines which spell slot table a class uses."""
    NONE = "none"
    FULL = "full"
    HALF = "half"
    THIRD = "third"
    PACT = "pact"


class ChoiceType(enum.Enum):
    SPELL = "spell"
    FEATURE = "feature"
    SKILL = "skill"
    EXPERTISE = "expertise"
    ABILITY = "ability"


class Recharge(enum.Enum):
    SHORT_REST = "short_rest"
    LONG_REST = "long_rest"
    NONE = "none"


class FeatCategory(enum.Enum):
    ORIGIN = "origin"
    GENERAL = "general"
    FIGHTING_STYLE = "fighting_style"
    EPIC_BOON = "epic_boon"


class FeatSource(enum.Enum):
    """Where a character's feat came from."""
    BACKGROUND = "background"
    ASI = "asi"
    SPECIES = "species"
    OTHER = "other"


class SpellSchool(enum.Enum):
    ABJURATION = "abjuration"
    CONJURATION = "conjuration"
    DIVINATION = "divination"
    ENCHANTMENT = "enchantment"
    EVOCATION = "evocation"
    ILLUSION = "illusion"
    NECROMANCY = "necromancy"
    TRANSMUTATION = "transmutation"


class AttackType(enum.Enum):
    MELEE = "melee"
    RANGED = "ranged"
