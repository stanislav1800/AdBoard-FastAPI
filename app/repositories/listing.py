
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .base import BaseRepository
from app.models import Category, ListingFavorite, ListingImage, Listing, StatusEnum
from app.schemas.listing import ListingCreate

class ListingRepository(BaseRepository[Listing]):
    m2m_fields = {"categories"}

    def _base_query(self):
        return (
            select(self.model)
            .options(
                selectinload(Listing.categories),
                selectinload(Listing.listing_images)
            )
        )
    
    async def create(self, obj_in: ListingCreate, user_id: int) -> Listing:
        data = obj_in.model_dump(exclude={"category_ids"})

        listing = Listing(**data, user_id=user_id)
        self.db.add(listing)

        if obj_in.category_ids:
            categories = await self.db.scalars(
                select(Category).where(Category.id.in_(obj_in.category_ids))
            )
            listing.categories = list(categories)

        await self.db.commit()

        listing = await self.db.scalar(
            self._base_query()
            .where(Listing.id == listing.id)
        )

        return listing
    
    async def get_listings(self, status: StatusEnum) -> list[Listing]:
        stmt = (
            select(Listing)
            .where(Listing.status == status)
            .options(
                selectinload(Listing.categories),
                selectinload(Listing.listing_images.and_(ListingImage.is_primary == True))
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def get_my_favorites(self, user_id):
        stmt = (
            self._base_query()
            .where(Listing.listing_favorites.any(ListingFavorite.user_id == user_id))
        )
        result = await self.db.execute(stmt)
        return result.scalars().all()
