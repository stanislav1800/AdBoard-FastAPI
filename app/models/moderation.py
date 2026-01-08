from datetime import datetime
from enum import Enum

from sqlalchemy import (
    DateTime,
    ForeignKey,
    func,
    Enum as SAEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class ActionEnum(str, Enum):
    ACTIVE = "active"
    REJECTED = "rejected"

class ModerationLog(Base):
    __tablename__ = "moderation_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))
    moderator_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[ActionEnum] = mapped_column(SAEnum(ActionEnum, name="action_enum"))
    reason: Mapped[str]
    # reason: Mapped[str] = mapped_column(
    #     nullable=True,
    # )
    create_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        default=datetime.now
    )

    listing: Mapped["Listing"] = relationship("Listing", back_populates="moderation_logs")
    moderator: Mapped["User"] = relationship("User", back_populates="moderation_logs")

    def __repr__(self) -> str:
        return f"<ModerationLog id={self.id} listing_id = {self.listing_id} moderator_id={self.moderator_id} action={self.action} reason={self.reason}>"
