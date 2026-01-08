from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .m2m import chat_participants


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(primary_key=True)
    participants: Mapped[list["User"]] = relationship(
    "User",
    secondary=chat_participants,
    back_populates="chats",
)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),    
    )

    listing: Mapped["Listing"] = relationship("Listing", back_populates="chats")
    messages: Mapped[list["Message"]] = relationship(back_populates="chat")

    def __repr__(self) -> str:
        return f"<Chat id={self.id} participants=[{self.participants}] listing_id = {self.listing_id}>"
