
from sqlalchemy import select, delete

from .base import BaseRepository
from app.models import ListingFavorite

class ListingFavoriteRepository(BaseRepository[ListingFavorite]):
    
    async def add(self, user_id: int, listing_id: int):
        exists = await self.db.execute(
            select(ListingFavorite).where(
                ListingFavorite.user_id == user_id,
                ListingFavorite.listing_id == listing_id,
            )
        )
        if exists.scalar():
            return

        self.db.add(
            ListingFavorite(
                user_id=user_id,
                listing_id=listing_id,
            )
        )
        await self.db.commit()

    async def remove(self, user_id: int, listing_id: int):
        await self.db.execute(
            delete(ListingFavorite).where(
                ListingFavorite.user_id == user_id,
                ListingFavorite.listing_id == listing_id,
            )
        )
        await self.db.commit()
