import json
from pathlib import Path

from ..models.Background import Background
from ..models.CharacterClass import CharacterClass
from ..models.Feat import Feat
from ..models.ModelBase import ModelBase
from ..models.Species import Species
from ..models.Subclass import Subclass

from sqlalchemy import Enum, inspect, select
from sqlalchemy.orm import Session

SRD_DIR = Path(__file__).resolve().parent.parent / "content" / "srd"

# Files to load, in dependency order (a file may only reference content loaded before it).
SRD_FILES: list[tuple[str, type[ModelBase]]] = [
    ("CharacterClasses.json", CharacterClass),
    ("Species.json", Species),
    ("Backgrounds.json", Background),
    ("Subclasses.json", Subclass),
]

# JSON fields that reference another model by its key, mapped to the foreign key column and model they resolve to.
KEY_REFERENCES: dict[str, tuple[str, type[ModelBase]]] = {
    "class_key": ("class_id", CharacterClass),
    "feat_key": ("feat_id", Feat),
}


def _read_entries(path: Path) -> list[dict]:
    """Reads a JSON file containing a list of entries. An empty file is treated as having no entries."""

    text = path.read_text(encoding="utf-8")
    if not text.strip():
        return []

    entries = json.loads(text)
    if not isinstance(entries, list) or not all(isinstance(entry, dict) for entry in entries):
        raise ValueError(f"{path.name}: expected a list of objects.")
    return entries


def _entry_to_values(entry: dict, model: type[ModelBase], filename: str, db: Session) -> dict:
    """Converts a JSON entry into column values for the model: resolves key references and converts enum values."""

    columns = inspect(model).columns
    values = {}

    for field, value in entry.items():
        if field in KEY_REFERENCES:
            column_name, referenced_model = KEY_REFERENCES[field]
            if column_name not in columns:
                raise ValueError(f"{filename}: '{field}' is not valid for {model.__name__}.")
            referenced = db.execute(select(referenced_model).where(referenced_model.key == value)).scalar_one_or_none()
            if referenced is None:
                raise ValueError(f"{filename}: '{field}' refers to {referenced_model.__name__} '{value}', which does not exist.")
            values[column_name] = referenced.id
        elif field in columns and field != "id":
            column_type = columns[field].type
            if value is not None and isinstance(column_type, Enum):
                try:
                    value = column_type.enum_class(value)
                except ValueError:
                    raise ValueError(f"{filename}: '{value}' is not a valid value for '{field}'.")
            values[field] = value
        else:
            raise ValueError(f"{filename}: unknown field '{field}' for {model.__name__}.")

    return values


def load_srd_content(db: Session) -> None:
    """Parses the JSON files in content/srd/ and ensures their entries are present in the database.

    Entries are matched on `key`: missing entries are created, and existing entries are updated to
    match the file, so the JSON files are the source of truth for SRD content. Nothing is deleted.
    Changes are committed together, so a bad entry leaves the database untouched.
    """

    try:
        for filename, model in SRD_FILES:
            for entry in _read_entries(SRD_DIR / filename):
                if "key" not in entry:
                    raise ValueError(f"{filename}: entry is missing 'key': {entry}")

                values = _entry_to_values(entry, model, filename, db)
                existing = db.execute(select(model).where(model.key == entry["key"])).scalar_one_or_none()

                if existing is None:
                    db.add(model(**values))
                else:
                    for field, value in values.items():
                        setattr(existing, field, value)

                db.flush()  # Later entries and files can reference this one by key
        db.commit()
    except Exception:
        db.rollback()
        raise
