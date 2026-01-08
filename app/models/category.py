from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .m2m import listing_categories

class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    order: Mapped[int]

    listings: Mapped[list["Listing"]] = relationship(
        secondary=listing_categories,
        back_populates="categories",
    )

    def __repr__(self) -> str:
        return f"<Category id={self.id} name = {self.name} slug={self.slug}>"