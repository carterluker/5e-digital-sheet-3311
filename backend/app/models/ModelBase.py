import enum

from sqlalchemy import Enum
from sqlalchemy.orm import DeclarativeBase

class ModelBase(DeclarativeBase):
    """DeclarativeBase subclass for model registry in metadata."""

    # Store Python enums as VARCHAR (+ CHECK) rather than native Postgres enum types,
    # so adding a value later doesn't require ALTER TYPE.
    type_annotation_map = {
        enum.Enum: Enum(enum.Enum, native_enum=False),
    }
