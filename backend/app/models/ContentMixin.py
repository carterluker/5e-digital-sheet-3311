from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column


class ContentMixin:
    """Columns shared by every character component (content) model.

    `key` is the stable tech name (e.g. "fighter", "fire_bolt") used by seed data and
    cross-references, separate from the player-facing `name`. `source` records the book
    or homebrew the content comes from (e.g. "PHB 2024").
    """
    # sort_order places these before the model's own columns in the table
    id: Mapped[int] = mapped_column(primary_key=True, sort_order=-1)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True, sort_order=-1)
    name: Mapped[str] = mapped_column(String(255), sort_order=-1)
    description: Mapped[str] = mapped_column(Text, default="", sort_order=-1)
    source: Mapped[str] = mapped_column(String(100), default="", sort_order=-1)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(key={self.key!r})"
