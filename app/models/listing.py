from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Integer,
    String,
    DateTime,
    Float,
    ForeignKey,
    Enum as SAEnum,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .m2m import listing_categories

# class ConditionEnum(int, Enum):
#     NEW = 1
#     USED = 2
#     EXCELLENT = 3

class ConditionEnum(str, Enum):
    NEW = "new"
    USED = "used"
    EXCELLENT = "excellent"

class StatusEnum(str, Enum):
    DRAFT = "draft"
    MODERATION = "moderation"
    REJECTED = "rejected"
    ACTIVE = "active"
    SOLD = "sold"
    ARCHIVED = "archived"
    DELETE = "delete"

class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    description: Mapped[str]
    price: Mapped[float] = mapped_column(Float, nullable=False)
    condition: Mapped[ConditionEnum] = mapped_column(
        SAEnum(ConditionEnum, name="condition_enum"),
        nullable=False,
    )
    # condition: Mapped[ConditionEnum] = mapped_column(
    #     Integer,
    #     nullable=False
    # )
    location: Mapped[str]
    status: Mapped[StatusEnum] = mapped_column(
        SAEnum(StatusEnum, name="status_enum"),
        nullable=False,
        default=StatusEnum.MODERATION
    )
    views_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    update_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
    )

    chats: Mapped[list["Chat"]] = relationship(
        "Chat",
        back_populates="listing",
        cascade="all, delete-orphan",
    )
    user: Mapped["User"] = relationship("User", back_populates="listings")
    categories: Mapped[list["Category"]] = relationship(
        secondary=listing_categories,
        back_populates="listings",
        lazy="selectin",
    )
    moderation_logs: Mapped[list["ModerationLog"]] = relationship(
        "ModerationLog",
        back_populates="listing",
        cascade="all, delete-orphan"
    )
    listing_favorites: Mapped[list["ListingFavorite"]] = relationship("ListingFavorite", back_populates="listing")
    listing_images: Mapped[list["ListingImage"]] = relationship("ListingImage", back_populates="listing")

    def __repr__(self) -> str:
        return f"<Listing id={self.id} user_id = {self.user_id} title={self.title[:20]} price={self.price} status={self.status}>"
