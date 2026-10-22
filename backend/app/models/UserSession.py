from datetime import datetime

from .ModelBase import ModelBase

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .User import User


class UserSession(ModelBase):
    """A login session. Only a hash of the session token is stored, never the token itself."""
    __tablename__ = "user_session"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"), index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True)  # SHA-256 hex digest
    created_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    expires_date: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship()

    def __repr__(self) -> str:
        return f"TODO"
