from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    Enum as SAEnum,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .m2m import chat_participants

class UserRoleEnum(str, Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

class CityEnum(str, Enum):
    MOSCOW = "Moscow"
    SAINT_PETERSBURG = "Saint Petersburg"
    NOVOSIBIRSK = "Novosibirsk"
    YEKATERINBURG = "Yekaterinburg"
    NIZHNY_NOVGOROD = "Nizhny Novgorod"
    KAZAN = "Kazan"
    CHELYABINSK = "Chelyabinsk"
    OMSK = "Omsk"
    SAMARA = "Samara"
    ROSTOV_ON_DON = "Rostov-on-Don"
    UFA = "Ufa"
    KRASNOYARSK = "Krasnoyarsk"
    PERM = "Perm"
    VORONEZH = "Voronezh"
    VOLGOGRAD = "Volgograd"
    KRASNODAR = "Krasnodar"
    SARATOV = "Saratov"
    TYUMEN = "Tyumen"
    TOLYATTI = "Tolyatti"
    IZHEVSK = "Izhevsk"
    BARNAUL = "Barnaul"
    ULYANOVSK = "Ulyanovsk"
    IRKUTSK = "Irkutsk"
    KHABAROVSK = "Khabarovsk"
    YAROSLAVL = "Yaroslavl"
    VLADIVOSTOK = "Vladivostok"
    MAKHACHKALA = "Makhachkala"
    TOMSK = "Tomsk"
    ORENBURG = "Orenburg"
    RYAZAN = "Ryazan"

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(150),
        unique=True,
        nullable=False,
    )
    password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    email: Mapped[Optional[str]] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )
    phone_number: Mapped[Optional[str]] = mapped_column(
        String(12),
        unique=True,
        nullable=True,
    )
    avatar: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        default="defaults/avatar.png",
    )
    role: Mapped[UserRoleEnum] = mapped_column(
        SAEnum(UserRoleEnum, name="user_role_enum"),
        nullable=False,
        default=UserRoleEnum.USER,
    )
    location: Mapped[Optional[CityEnum]] = mapped_column(
        SAEnum(CityEnum, name="city_enum"),
        nullable=True,
    )
    bio: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    last_seen: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    listings: Mapped[list["Listing"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    chats: Mapped[list["Chat"]] = relationship(
        "Chat",
        secondary=chat_participants,
        back_populates="participants",
    )
    ratings_received: Mapped[list["UserRating"]] = relationship(
        "UserRating",
        foreign_keys="UserRating.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    ratings_given: Mapped[list["UserRating"]] = relationship(
        "UserRating",
        foreign_keys="UserRating.rater_id",
        back_populates="rater",
        cascade="all, delete-orphan",
    )
    moderation_logs: Mapped[list["ModerationLog"]] = relationship(back_populates="moderator")
    listing_favorites: Mapped["ListingFavorite"] = relationship("ListingFavorite", back_populates="user")
    messages: Mapped[list["Message"]] = relationship(back_populates="sender")

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username}>"
