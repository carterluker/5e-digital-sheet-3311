from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from .. import actions, rules
from ..config import settings
from ..db import get_db
from ..models import Character, CharacterBackup, User, as_utc, utcnow
from ..schemas import (
    ActionRequest,
    ActionResult,
    BackupSummary,
    CharacterCreate,
    CharacterOut,
    CharacterSave,
    CharacterSummary,
)
from ..security import current_user
from ..sheet import LayoutItem, Sheet

router = APIRouter(prefix="/api/characters", tags=["characters"])


# ------------------------------------------------------------------ helpers

def get_owned(db: Session, user: User, character_id: int) -> Character:
    char = db.get(Character, character_id)
    if char is None or char.owner_id != user.id:  # same response either way: don't leak existence
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Character not found")
    return char


def to_out(char: Character) -> CharacterOut:
    sheet = Sheet.model_validate(char.data)
    return CharacterOut(
        id=char.id,
        name=char.name,
        version=char.version,
        data=sheet,
        layout=[LayoutItem.model_validate(i) for i in char.layout],
        derived=rules.derive(sheet),
        issues=rules.validate(sheet),
        created_at=char.created_at,
        updated_at=char.updated_at,
    )


def snapshot(db: Session, char: Character, reason: str) -> None:
    """Store the character's current state as a backup, then prune the oldest ones."""
    db.add(CharacterBackup(character_id=char.id, version=char.version, reason=reason, data=char.data, layout=char.layout))
    db.flush()
    stale = db.scalars(
        select(CharacterBackup)
        .where(CharacterBackup.character_id == char.id)
        .order_by(CharacterBackup.id.desc())
        .offset(settings.max_backups_per_character)
    ).all()
    for b in stale:
        db.delete(b)


def backup_due(db: Session, char: Character) -> bool:
    newest = db.scalar(
        select(CharacterBackup.created_at)
        .where(CharacterBackup.character_id == char.id)
        .order_by(CharacterBackup.id.desc())
        .limit(1)
    )
    return newest is None or utcnow() - as_utc(newest) >= timedelta(seconds=settings.backup_interval_seconds)


def persist(db: Session, char: Character, sheet: Sheet, layout: list | None, expected_version: int | None, reason: str = "autosave") -> Character:
    """Write a new state with optimistic locking, backing up the previous state when due."""
    if expected_version is not None and expected_version != char.version:
        raise HTTPException(status.HTTP_409_CONFLICT, f"Version conflict: server has version {char.version}, client sent {expected_version}")
    if backup_due(db, char):
        snapshot(db, char, reason)
    result = db.execute(
        update(Character)
        .where(Character.id == char.id, Character.version == char.version)
        .values(
            name=sheet.name,
            data=sheet.model_dump(mode="json"),
            layout=char.layout if layout is None else [i.model_dump(mode="json") for i in layout],
            version=char.version + 1,
            updated_at=utcnow(),
        )
        .execution_options(synchronize_session=False)
    )
    if result.rowcount != 1:  # a concurrent writer got in first
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Version conflict: character was modified concurrently")
    db.commit()
    db.refresh(char)
    return char


# ------------------------------------------------------------------- CRUD

@router.get("", response_model=list[CharacterSummary])
def list_characters(user: User = Depends(current_user), db: Session = Depends(get_db)):
    chars = db.scalars(select(Character).where(Character.owner_id == user.id).order_by(Character.updated_at.desc(), Character.id.desc()))
    return [
        CharacterSummary(
            id=c.id,
            name=c.name,
            race=c.data.get("race", ""),
            character_class=c.data.get("character_class", ""),
            level=c.data.get("level", 1),
            version=c.version,
            updated_at=c.updated_at,
        )
        for c in chars
    ]


@router.post("", response_model=CharacterOut, status_code=status.HTTP_201_CREATED)
def create_character(body: CharacterCreate, user: User = Depends(current_user), db: Session = Depends(get_db)):
    char = Character(
        owner_id=user.id,
        name=body.data.name,
        data=body.data.model_dump(mode="json"),
        layout=[i.model_dump(mode="json") for i in body.layout],
    )
    db.add(char)
    db.commit()
    db.refresh(char)
    return to_out(char)


@router.get("/{character_id}", response_model=CharacterOut)
def read_character(character_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return to_out(get_owned(db, user, character_id))


@router.put("/{character_id}", response_model=CharacterOut)
def autosave(character_id: int, body: CharacterSave, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Save the sheet. Rule violations never block a save (so autosave can't lose
    work); they are reported in the response's `issues`."""
    char = get_owned(db, user, character_id)
    return to_out(persist(db, char, body.data, body.layout, body.version))


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_character(character_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    db.delete(get_owned(db, user, character_id))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# --------------------------------------------------------- rules + bookkeeping

@router.post("/validate", response_model=dict)
def validate_sheet(sheet: Sheet, user: User = Depends(current_user)):
    """Stateless dry run: derived stats and rule issues for a sheet, nothing stored."""
    return {"derived": rules.derive(sheet).model_dump(), "issues": [i.model_dump() for i in rules.validate(sheet)]}


@router.post("/{character_id}/actions", response_model=ActionResult)
def run_action(character_id: int, body: ActionRequest, user: User = Depends(current_user), db: Session = Depends(get_db)):
    char = get_owned(db, user, character_id)
    sheet = Sheet.model_validate(char.data)
    try:
        messages = actions.apply(sheet, body.action)
    except actions.ActionError as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_CONTENT, str(e))
    char = persist(db, char, sheet, None, body.version, reason="autosave")
    return ActionResult(messages=messages, character=to_out(char))


# ------------------------------------------------------------------ backups

@router.get("/{character_id}/backups", response_model=list[BackupSummary])
def list_backups(character_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    char = get_owned(db, user, character_id)
    rows = db.scalars(select(CharacterBackup).where(CharacterBackup.character_id == char.id).order_by(CharacterBackup.id.desc()))
    return [BackupSummary(id=b.id, version=b.version, reason=b.reason, name=b.data.get("name", ""), created_at=b.created_at) for b in rows]


@router.post("/{character_id}/backups", response_model=BackupSummary, status_code=status.HTTP_201_CREATED)
def create_backup(character_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    char = get_owned(db, user, character_id)
    snapshot(db, char, "manual")
    db.commit()
    b = db.scalar(select(CharacterBackup).where(CharacterBackup.character_id == char.id).order_by(CharacterBackup.id.desc()).limit(1))
    return BackupSummary(id=b.id, version=b.version, reason=b.reason, name=b.data.get("name", ""), created_at=b.created_at)


def _get_backup(db: Session, char: Character, backup_id: int) -> CharacterBackup:
    b = db.get(CharacterBackup, backup_id)
    if b is None or b.character_id != char.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Backup not found")
    return b


@router.get("/{character_id}/backups/{backup_id}", response_model=Sheet)
def read_backup(character_id: int, backup_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return Sheet.model_validate(_get_backup(db, get_owned(db, user, character_id), backup_id).data)


@router.post("/{character_id}/backups/{backup_id}/restore", response_model=CharacterOut)
def restore_backup(character_id: int, backup_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    """Replace the live character with a backup. The state being replaced is backed up first."""
    char = get_owned(db, user, character_id)
    b = _get_backup(db, char, backup_id)
    snapshot(db, char, "pre-restore")  # always, regardless of the autosave interval
    result = db.execute(
        update(Character)
        .where(Character.id == char.id, Character.version == char.version)
        .values(name=b.data.get("name", char.name), data=b.data, layout=b.layout, version=char.version + 1, updated_at=utcnow())
        .execution_options(synchronize_session=False)
    )
    if result.rowcount != 1:
        db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "Version conflict: character was modified concurrently")
    db.commit()
    db.refresh(char)
    return to_out(char)
