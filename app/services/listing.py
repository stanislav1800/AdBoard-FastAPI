from typing import Annotated, Optional

from fastapi import Depends, BackgroundTasks

from app.core.exceptions import ListingAlreadyDeletedException, ListingAlreadyFavoriteException, ListingAlreadyModerateException, ListingNotFoundException, UserNotAccessException
from app.models import User, UserRoleEnum, Listing, StatusEnum
from app.repositories import (ListingFavoriteRepositoryDep,
    ListingRepositoryDep,
    ModerationLogRepositoryDep,
    ListingRepository,
    ListingFavoriteRepository,
    ModerationLogRepository,
)
from app.schemas.listing import ListingPatch
from app.services.listing_image import ListingImageService, ListingImageServiceDep
from app.services.email import EmailService

class ListingService:
    def __init__(
        self,
        listing_repo:  ListingRepository,
        favorite_repo: ListingFavoriteRepository,
        image_service: ListingImageService,
        moderation_repo: ModerationLogRepository,
    ):
        self.listing_repo = listing_repo
        self.favorite_repo = favorite_repo
        self.image_service = image_service
        self.moderation_repo = moderation_repo

    async def get_or_404(self, id: int):
        listing = await self.listing_repo.get_by_id(id)
        if not listing:
            raise ListingNotFoundException
        return listing

    async def ensure_owner(self, listing: Listing, user: User):
        if listing.user_id == user.id or user.role == UserRoleEnum.ADMIN:
            return listing
        raise UserNotAccessException

    async def ensure_public(self, listing: Listing, user: User | None):
        if user and listing.user_id == user.id:
            return listing
        if listing.status != StatusEnum.ACTIVE:
            raise ListingNotFoundException
        return listing

    async def ensure_moderator(self, listing: Listing, user: User):
        if user.role not in {UserRoleEnum.MODERATOR, UserRoleEnum.ADMIN}:
            raise UserNotAccessException
        return listing

    async def for_favorite(self, listing: Listing, user: User):
        if not listing:
            raise ListingNotFoundException
        return listing
    
    async def get_published(self):
        return await self.listing_repo.get_by_filters(status=StatusEnum.ACTIVE)
    
    async def get_my_listings(self, user_id: int):
        return await self.listing_repo.get_by_filters(user_id=user_id)
    
    async def get_moderation_listings(self, user: User):
        if user.role not in {UserRoleEnum.ADMIN, UserRoleEnum.MODERATOR}:
            raise UserNotAccessException
        return await self.listing_repo.get_by_filters(status=StatusEnum.MODERATION)
    
    async def get_favorites(self, user_id: int):
        return await self.listing_repo.get_my_favorites(user_id)

    async def get_all(self, user: User):
        if user.role != UserRoleEnum.ADMIN:
            raise UserNotAccessException
        return await self.listing_repo.get_all()
    
    async def create_listing(self, user: User, data):
        return await self.listing_repo.create(data, user_id=user.id)

    async def upload_images(self, listing: Listing, files):
        return await self.image_service.upload(listing, files)

    async def get_image(self, image_id: int):
        return await self.image_service.get_image(image_id)

    async def make_primary(self, listing: Listing, image_id: int):
        return await self.image_service.set_primary(listing.id, image_id)

    async def delete_image(self, image_id: int, user: User):
        image = await self.image_service.get_image(image_id)
        if image.listing.user_id != user.id:
            raise UserNotAccessException
        return await self.image_service.delete_image(image)

    async def moderate(
        self,
        listing: Listing,
        data,
        user: User,
        background_tasks: BackgroundTasks,
    ):
        if listing.status != StatusEnum.MODERATION:
            raise ListingAlreadyModerateException

        form_data = ListingPatch(status=data.action)
        updated = await self.listing_repo.update(listing, form_data, exclude_unset=True)

        data.moderator_id = user.id
        data.listing_id = listing.id
        log = await self.moderation_repo.create(data)

        # собираем email шаблон
        subject = "Ваше объявление прошло модерацию"
        if data.action == StatusEnum.REJECTED:
            subject = "Ваше объявление отклонено на модерации"
            
        body = f"""
            <p>Здравствуйте!</p>
            <p>Ваше объявление <strong>{listing.title}</strong> 
            было проверено модератором.</p>
            <p>Результат: <strong>{data.action.name.lower()}</strong>.</p>
        """

        if listing.user.email:
            email_service = EmailService()
            background_tasks.add_task(
                email_service.send,
                recipients=[listing.user.email],
                subject=subject,
                body=body,
            )
            
        return log

    async def add_favorite(self, listing: Listing, user: User):
        existing = await self.favorite_repo.get_by_filters(
            user_id=user.id, listing_id=listing.id
        )
        if existing:
            raise ListingAlreadyFavoriteException
        return await self.favorite_repo.add(user.id, listing.id)

    async def remove_favorite(self, listing: Listing, user: User):
        return await self.favorite_repo.remove(user.id, listing.id)

    async def get_listing_detail(self, listing: Listing, user: Optional[User]):
        return await self.listing_repo.get_detail(listing.id)

    async def update_listing(self, listing: Listing, data, exclude_unset: bool = False):
        return await self.listing_repo.update(listing, data, exclude_unset=exclude_unset)

    async def delete_listing(self, listing: Listing):
        if listing.status == StatusEnum.DELETE:
            raise ListingAlreadyDeletedException

        for image in listing.listing_images:
            await self.image_service.delete_image(image)

        form_data = ListingPatch(status=StatusEnum.DELETE)
        listing = await self.listing_repo.update(listing, form_data, exclude_unset=True)

def get_listing_service(
    listing_repo: ListingRepositoryDep,
    favorite_repo: ListingFavoriteRepositoryDep,
    moderation_repo: ModerationLogRepositoryDep,
    image_service: ListingImageServiceDep,
) -> ListingService:
    return ListingService(
        listing_repo=listing_repo,
        favorite_repo=favorite_repo,
        image_service=image_service,
        moderation_repo=moderation_repo,
    )

ListingServiceDep = Annotated[ListingService, Depends(get_listing_service)]
