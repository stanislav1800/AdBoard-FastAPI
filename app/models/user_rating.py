from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class UserRating(Base):
    __tablename__ = "user_rating"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    rater_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    score: Mapped[float] = mapped_column(
        Float,
    )
    comment: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    user: Mapped["User"] = relationship("User", foreign_keys=[user_id], back_populates="ratings_received")
    rater: Mapped["User"] = relationship("User", foreign_keys=[rater_id], back_populates="ratings_given")

    def __repr__(self) -> str:
        return f"UserRating(id={self.id!r}, user={self.user_id!r}, rater={self.rater_id!r}, score={self.score})"