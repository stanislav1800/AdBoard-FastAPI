
from fastapi import APIRouter, status, UploadFile, File, BackgroundTasks

from app.schemas import ListingDetail
from app.schemas.listing import ListingCreate, ListingPatch, ListingPut
from app.schemas.listing_image import ListingImageDetail
from app.schemas.moderation import ModerationLogCreate, ModerationLogDetail
from app.api.deps import AdminDep, CurrentUserOptionalDep, ListingForFavoriteDep, UserDep, ListingModerateDep, ListingOwnerDep, ListingPublicDep
from app.services.listing import ListingServiceDep


router = APIRouter()

@router.get(
    "/published",
    response_model=list[ListingDetail],
    summary="Список опубликованных объявлений",
)
async def get_published_listings(
    listing_service: ListingServiceDep,
):
    return await listing_service.get_published()

@router.get(
    "/my_listings",
    response_model=list[ListingDetail],
    summary="Мои объявления",
)
async def get_my_listings_listings(
    user: UserDep,
    listing_service: ListingServiceDep,
):
    return await listing_service.get_my_listings(user.id)

@router.get(
    "/moderation",
    response_model=list[ListingDetail],
    summary="Список объявлений на модерации",
)
async def get_moderation_listings(
    user: UserDep,
    listing_service: ListingServiceDep,
):
    return await listing_service.get_moderation_listings(user)

@router.get(
    "/favorites",
    response_model=list[ListingDetail],
    summary="Мои избранные объявления",
)
async def get_my_favorites_listings(
    user: UserDep,
    listing_service: ListingServiceDep,
):
    return await listing_service.get_favorites(user.id)

@router.get(
    '',
    response_model=list[ListingDetail],
    summary="Получаем список объявлений",
)
async def get_list_listings(
    user: AdminDep,
    listing_service: ListingServiceDep,
):
    return await listing_service.get_all(user)


@router.post(
    '',
    response_model=ListingDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Создаем новое объявление",
)
async def create_listing(
    user: UserDep,
    listing_service: ListingServiceDep,
    form: ListingCreate,
):
    return await listing_service.create_listing(user, form)


@router.post(
    "/{id}/images",
    response_model=list[ListingImageDetail],
    status_code=status.HTTP_201_CREATED,
    summary="Добавить изображения к объявлению",
)
async def upload_images(
    listing: ListingOwnerDep,
    listing_service: ListingServiceDep,
    files: list[UploadFile] = File(...),
):
    return await listing_service.upload_images(listing, files)

@router.get(
    "/{image_id}/images",
    response_model=ListingImageDetail
)
async def get_listing_image(
    image_id: int,
    user: CurrentUserOptionalDep,
    listing_service: ListingServiceDep,
):
    return await listing_service.get_image(image_id, user)

@router.post(
    "/{id}/images/{image_id}/primary",
    status_code=status.HTTP_201_CREATED,
    summary="Обновление изображения превью",
)
async def make_primary(
    listing: ListingOwnerDep,
    image_id: int,
    listing_service: ListingServiceDep,
):
    return await listing_service.make_primary(listing, image_id)

@router.delete(
    "/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление изображения",
)
async def delete_image(
    image_id: int,
    user: UserDep,
    listing_service: ListingServiceDep,
):
    return await listing_service.delete_image(image_id, user)


@router.post(
    '/{id}/moderated',
    response_model=ModerationLogDetail,
    status_code=status.HTTP_201_CREATED,
    summary="Модерация объявления",
)
async def change_moderate(
    listing: ListingModerateDep,
    form: ModerationLogCreate,
    user: UserDep,
    listing_service: ListingServiceDep,
    background_tasks: BackgroundTasks,
):
    return await listing_service.moderate(listing, form, user, background_tasks)

@router.post(
    '/{id}/favorites',
    status_code=status.HTTP_201_CREATED,
    summary="Добавить объявление в избранное",
)
async def add_favorites(
    listing: ListingForFavoriteDep,
    user: UserDep,
    listing_service: ListingServiceDep,
):
    return await listing_service.add_favorite(listing, user)

@router.delete(
    '/{id}/favorites',
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удалить объявление из избранного",
)
async def delete_favorites(
    listing: ListingForFavoriteDep,
    user: CurrentUserOptionalDep,
    listing_service: ListingServiceDep,
):
    return await listing_service.remove_favorite(listing, user)


@router.get(
    "/{id}",
    response_model=ListingDetail,
    summary="Получаем объявление",
)
async def get_listing(
    listing: ListingPublicDep,
    user: CurrentUserOptionalDep,
    listing_service: ListingServiceDep,
):
    return await listing_service.get_listing_detail(listing, user)

@router.put(
    "/{id}",
    response_model=ListingDetail,
    summary="Полное обновление объявления",
)
async def update_listing(
    listing: ListingOwnerDep,
    form: ListingPut,
    listing_service: ListingServiceDep,
):
    return await listing_service.update_listing(listing, form)

@router.patch(
    "/{id}",
    response_model=ListingDetail,
    summary="Частичное обновление объявления",
)
async def patch_listing(
    listing: ListingOwnerDep,
    form: ListingPatch,
    listing_service: ListingServiceDep,
):
    return await listing_service.update_listing(listing, form, exclude_unset=True)

@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление объявления",
)
async def delete_listing(
    listing: ListingOwnerDep,
    listing_service: ListingServiceDep,
):
    return await listing_service.delete_listing(listing)
