
from sqlalchemy import select, update

from .base import BaseRepository
from app.models import ListingImage

class ListingImageRepository(BaseRepository[ListingImage]):

    async def create_many(self, images: list[ListingImage]):
        self.db.add_all(images)
        await self.db.commit()
        for img in images:
            await self.db.refresh(img)
        return images

    # async def delete(self, image_id: int):
    #     stmt = select(ListingImage).where(ListingImage.id == image_id)
    #     result = await self.db.execute(stmt)
    #     image = result.scalar_one_or_none()
    #     if not image:
    #         return None
    #     await self.db.delete(image)
    #     await self.db.commit()
    #     return image

    async def get_primary(self, listing_id: int) -> ListingImage | None:
        stmt = select(ListingImage).where(
            ListingImage.listing_id == listing_id,
            ListingImage.is_primary == True
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def set_primary(self, listing_id: int, image_id: int):
        await self.db.execute(
            update(ListingImage)
            .where(ListingImage.listing_id == listing_id, ListingImage.is_primary == True)
            .values(is_primary=False)
        )
        await self.db.execute(
            update(ListingImage)
            .where(ListingImage.id == image_id)
            .values(is_primary=True)
        )
        await self.db.commit()
    
    async def delete_image(self, image_id: int):
        image = await self.get_by_id(image_id)
        if not image:
            return None

        await self.delete(image)

        return image