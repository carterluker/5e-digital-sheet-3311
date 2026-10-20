"""Request/response models for the HTTP API."""
import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from .actions import Action
from .rules import Derived, Issue
from .sheet import LayoutItem, Sheet


class Credentials(BaseModel):
    username: str = Field(min_length=3, max_length=32)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("username")
    @classmethod
    def _username(cls, v: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", v):
            raise ValueError("username may only contain letters, digits, '_', '.' and '-'")
        return v.lower()


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str


def _unique_layout(v: list[LayoutItem]) -> list[LayoutItem]:
    if len({i.id for i in v}) != len(v):
        raise ValueError("layout panel ids must be unique")
    return v


class CharacterCreate(BaseModel):
    data: Sheet = Sheet()
    layout: list[LayoutItem] = []

    _layout = field_validator("layout")(_unique_layout)


class CharacterSave(BaseModel):
    """Autosave payload. `version` is the version the client last saw."""

    version: int
    data: Sheet
    layout: list[LayoutItem] | None = None  # omit to leave the layout unchanged

    _layout = field_validator("layout")(lambda v: v if v is None else _unique_layout(v))


class ActionRequest(BaseModel):
    action: Action
    version: int | None = None  # optional optimistic-concurrency check


class CharacterSummary(BaseModel):
    id: int
    name: str
    race: str
    character_class: str
    level: int
    version: int
    updated_at: datetime


class CharacterOut(BaseModel):
    id: int
    name: str
    version: int
    data: Sheet
    layout: list[LayoutItem]
    derived: Derived
    issues: list[Issue]
    created_at: datetime
    updated_at: datetime


class ActionResult(BaseModel):
    messages: list[str]
    character: CharacterOut


class BackupSummary(BaseModel):
    id: int
    version: int
    reason: str
    name: str
    created_at: datetime
