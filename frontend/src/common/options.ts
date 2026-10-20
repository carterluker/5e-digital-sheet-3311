// Choices for the Basics dropdowns. Values match the backend's SRD tables (rules.py),
// so picking from these never triggers the "not an SRD class/race" warnings.

export const RACES = ["Dragonborn", "Dwarf", "Elf", "Gnome", "Half-Elf", "Half-Orc", "Halfling", "Human", "Tiefling"]

export const CLASSES = [
    "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard",
]

// SRD subclasses, keyed by lower-case class name.
export const SUBCLASSES: Record<string, string[]> = {
    barbarian: ["Path of the Berserker"],
    bard: ["College of Lore"],
    cleric: ["Life Domain"],
    druid: ["Circle of the Land"],
    fighter: ["Champion"],
    monk: ["Way of the Open Hand"],
    paladin: ["Oath of Devotion"],
    ranger: ["Hunter"],
    rogue: ["Thief"],
    sorcerer: ["Draconic Bloodline"],
    warlock: ["The Fiend"],
    wizard: ["School of Evocation"],
}

export const BACKGROUNDS = [
    "Acolyte", "Charlatan", "Criminal", "Entertainer", "Folk Hero", "Guild Artisan", "Hermit",
    "Noble", "Outlander", "Sage", "Sailor", "Soldier", "Urchin",
]

export const ALIGNMENTS = [
    "Lawful Good", "Neutral Good", "Chaotic Good",
    "Lawful Neutral", "True Neutral", "Chaotic Neutral",
    "Lawful Evil", "Neutral Evil", "Chaotic Evil",
]
