from typing import Annotated

from fastapi import Depends, UploadFile

from app.core.exceptions import ImageNotFoundException, UserNotAccessException
from app.models import Listing, ListingImage
from app.repositories import ListingImageRepositoryDep, ListingImageRepository
from app.storage.local import LocalStorage

class ListingImageService:
    def __init__(
            self,
            repo: ListingImageRepository,
            storage: LocalStorage
        ):
        self.repo = repo
        self.storage = storage

    async def get_image(self, image_id: int):
        image = await self.repo.get_by_id(image_id)
        if not image:
            raise ImageNotFoundException
        return image

    async def upload(self, listing: Listing, files: list[UploadFile]):
        """Загрузка изображений с установкой primary по умолчанию для первого"""
        last_order = len(await self.repo.get_by_filters(listing_id=listing.id))
        images = []

        for i, file in enumerate(files, start=1):
            path = await self.storage.save(file)
            images.append(ListingImage(
                listing_id=listing.id,
                image=path,
                order=last_order + i,
                is_primary=(last_order == 0 and i == 1)
            ))

        await self.repo.create_many(images)
        return images

    async def set_primary(self, listing_id: int, image_id: int):
        """Сделать изображение primary"""
        image = await self.get_image(image_id)
        if image.listing_id != listing_id:
            raise ImageNotFoundException
        await self.repo.set_primary(listing_id, image_id)

    async def delete_image(self, image: ListingImage):
        """Удаление изображения + удаление файла"""
        await self.storage.delete(image.image)
        await self.repo.delete(image)

def get_listing_image_service(
    repo: ListingImageRepositoryDep,
) -> ListingImageService:
    return ListingImageService(repo=repo, storage=LocalStorage())

ListingImageServiceDep = Annotated[ListingImageService, Depends(get_listing_image_service)]
