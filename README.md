# 5e Digital Character Sheet

React (TS) + Vite, FastAPI, PostgreSQL.

## Run
```
cp .env.example .env
docker compose up -d                                  # Postgres
cd backend && uv run uvicorn app.main:app --reload    # API on :8000
cd frontend && npm install && npm run dev             # UI on :5173 (proxies /api)
```

## Character Model Overview

The goal is to create an extensible database of Dungeons & Dragons 5.5e character components, such as Classes, Species, Feats, Spells, etc. that are presented to the user an organizable digital "character sheet".

All bookkeeping is handled by the application, so that users don't need to worry about handling items such as calculating ability score modifier, skill-check bonuses, attack bonus, etc.

### Character Component Models

This model of character components was selected to support easy addition of new content. Older prototypes of this program used entirely hand-written scripts to validate a sheet, rather than building the sheet itself.

This specific model was inspired by the Baldurs Gate 3 Modding Toolkit. BG3 equivalents are noted in parentheses.

Every content model shares a stable `key` (tech name used by seed data and cross-references), `name`, `description` and `source` (e.g. "PHB 2024", or homebrew).

#### Content Models

- **CharacterClass** (ClassDescriptions): A class that a character can take, such as "Wizard" or "Barbarian". Holds static facts: hit die, primary abilities, saving throws, spellcasting ability and caster type, subclass level, multiclass prerequisites.
- **Subclass** (ClassDescriptions with ParentUUID): A subclass that provides features in addition to those provided by its parent CharacterClass.
- **Species** (Races): Size, speed, creature type, and species traits via its Progression.
- **Background**: Ability score options, origin Feat, skill and tool proficiencies, equipment.
- **Progression** (Progressions): What a CharacterClass, Subclass or Species grants at a given level. One table serves all three.
  - **effects**: Automatic grants such as proficiencies, resources and ability bonuses (Boosts).
  - **ProgressionFeature**: Features granted at that level (PassivesAdded).
  - **ProgressionChoice**: Choices the player makes at that level, such as "Choose a Fighting Style" or "Learn 2 Wizard cantrips" (Selectors).
  - Flags for when an Ability Score Improvement/Feat or Subclass is gained (AllowImprovement, SubClasses).
- **Feature** (Passives): A named feature such as Rage, Darkvision or Second Wind, with its effects and the Resource it uses.
- **Resource** (ActionResources): A limited-use resource such as Rage or Spell Slots, and when it recharges.
- **Feat**: Optional features taken from a Background or an Ability Score Improvement. Has a category, prerequisites, effects, and its own choices.
- **Spell** (Spell stats): Level, school, casting time, range, components, duration, concentration, attack or saving throw, damage.
- **SpellList / FeatureList** (SpellLists, PassiveLists): Reusable sets of Spells or Features that a ProgressionChoice picks from.

#### Character Models

The six ability scores are stored as base scores. Modifiers, proficiency bonus, saving throws, skill bonuses, etc. are always computed from the models below, never stored.

- **Character**: Name, base ability scores, Species, Background, HP, experience, etc.
- **CharacterClassLevel**: Levels taken in each CharacterClass/Subclass, supporting multiclassing.
- **CharacterSelection**: What the player picked for each ProgressionChoice.
- **CharacterFeat**: Feats the character has taken, and where they came from.
- **CharacterResourceState**: Current usage of each Resource. The maximum is computed.

## Sources

- [BG3 Toolkit: Main Page](https://docs.baldursgate3.game/index.php?title=Main_Page)
- [BG3 Toolkit: Adding Classes and Subclasses](https://docs.baldursgate3.game/index.php?title=Adding_Classes_and_Subclasses)
- [BG3 Toolkit: Making a Basic Spell](https://docs.baldursgate3.game/index.php?title=Making_a_Basic_Spell)
- [bg3.wiki: Modding: LSX files](https://bg3.wiki/wiki/Modding:LSX_files)
- [BG3 Compatibility Framework: Selector API](https://github.com/BG3-Community-Library-Team/BG3-Compatibility-Framework/wiki/_Selector-API)
