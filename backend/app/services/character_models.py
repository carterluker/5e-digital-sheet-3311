from fastapi import Depends, HTTPException, status

from ..db.db import get_db

from ..models.Background import Background
from ..models.CharacterClass import CharacterClass
from ..models.Feat import Feat
from ..models.Species import Species
from ..models.Spell import Spell
from ..models.Subclass import Subclass

from sqlalchemy import select
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session


def _list_models(statement, db: Session) -> list:
    """Executes the given select statement and returns every resulting model."""

    try:
        return list(db.execute(statement).scalars().all())
    except OperationalError:
        # Database is down or timed out: 503
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The backend database is unavailable."
        )


def get_character_classes(db: Session = Depends(get_db)) -> list[CharacterClass]:
    """Retrieves every CharacterClass, ordered by name."""

    return _list_models(select(CharacterClass).order_by(CharacterClass.name), db)


def get_subclasses(class_id: int, db: Session = Depends(get_db)) -> list[Subclass]:
    """Retrieves every Subclass of the CharacterClass with the given id, ordered by name."""

    return _list_models(select(Subclass).where(Subclass.class_id == class_id).order_by(Subclass.name), db)


def get_species(db: Session = Depends(get_db)) -> list[Species]:
    """Retrieves every Species, ordered by name."""

    return _list_models(select(Species).order_by(Species.name), db)


def get_backgrounds(db: Session = Depends(get_db)) -> list[Background]:
    """Retrieves every Background, ordered by name."""

    return _list_models(select(Background).order_by(Background.name), db)


def get_feats(db: Session = Depends(get_db)) -> list[Feat]:
    """Retrieves every Feat, ordered by name."""

    return _list_models(select(Feat).order_by(Feat.name), db)


def get_spells(db: Session = Depends(get_db)) -> list[Spell]:
    """Retrieves every Spell, ordered by level and then name."""

    return _list_models(select(Spell).order_by(Spell.level, Spell.name), db)
