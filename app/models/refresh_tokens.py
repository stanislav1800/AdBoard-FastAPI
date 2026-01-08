from datetime import datetime

from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    func,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now()
    )
    revoked: Mapped[bool] = mapped_column(Boolean, default=False)
