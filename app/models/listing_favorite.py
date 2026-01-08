from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

class ListingFavorite(Base):
    __tablename__ = "listing_favorites"

    id: Mapped[int] = mapped_column(primary_key=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    listing: Mapped["Listing"] = relationship("Listing", back_populates='listing_favorites')
    user: Mapped["User"] = relationship("User", back_populates='listing_favorites')

    def __repr__(self) -> str:
        return f"<ListingFavorite id={self.id} listing_id = {self.listing_id} user_id={self.user_id}>"
