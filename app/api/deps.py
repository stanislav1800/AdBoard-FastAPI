from typing import Annotated, Optional

from fastapi import Depends, WebSocket
from fastapi.security import OAuth2PasswordBearer
import jwt

from app.core.config import settings
from app.core.exceptions import InvalidAuthenticationCredentialsException, TokenInvalidException, UserIsNotPresentException, UserNotAccessException, UserNotFoundException
from app.models import Listing, User, UserRoleEnum
from app.repositories import UserRepository
from app.services.auth import AuthServiceDep
from app.services.listing import ListingServiceDep


oauth2_scheme_required = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token", auto_error=False)

async def get_current_user(
    auth: AuthServiceDep,
    token: str = Depends(oauth2_scheme_required),
) -> User:
    try:
        user = await auth.get_user_from_token(token)
    except jwt.PyJWTError:
        raise InvalidAuthenticationCredentialsException
    
    if not user:
        raise UserIsNotPresentException
    return user

async def get_current_user_optional(
    auth: AuthServiceDep,
    token: Annotated[str | None, Depends(oauth2_scheme_optional)],
) -> Optional[User]:
    if not token:
        return None
    user = await auth.get_user_from_token(token)
    return user

def require_roles(*roles: UserRoleEnum):
    async def _dependency(user: User = Depends(get_current_user)):
        if user.role not in roles:
            raise UserNotAccessException
        return user
    return Depends(_dependency)

UserDep = Annotated[User, Depends(get_current_user)]
AdminDep = Annotated[User, require_roles(UserRoleEnum.ADMIN)]
CurrentUserOptionalDep = Annotated[Optional[User], Depends(get_current_user_optional)]


async def get_current_user_ws(
    auth: AuthServiceDep,
    ws: WebSocket,
    db: UserRepository,
    token: str
) -> User:
    if not token:
        await ws.close(code=1008)
        raise TokenInvalidException
    
    user = await auth.get_user_from_token(token)
    if not user:
        await ws.close(code=1008)
        raise UserNotFoundException
    return user


async def get_listing_or_404(
    id: int,
    listing_service: ListingServiceDep,
):
    return await listing_service.get_or_404(id)

async def listing_owner_required(
    user: UserDep,
    listing_service: ListingServiceDep,
    listing: Listing = Depends(get_listing_or_404),
):
    return await listing_service.ensure_owner(listing, user)

async def get_public_listing_or_404(
    user: CurrentUserOptionalDep,
    listing_service: ListingServiceDep,
    listing: Listing = Depends(get_listing_or_404),
):
    return await listing_service.ensure_public(listing, user)

async def listing_moderator_required(
    user: UserDep,
    listing_service: ListingServiceDep,
    listing: Listing = Depends(get_listing_or_404),
):
    return await listing_service.ensure_moderator(listing, user)

async def get_listing_for_favorite(
    user: UserDep,
    listing_service: ListingServiceDep,
    listing: Listing = Depends(get_listing_or_404),
):
    return await listing_service.for_favorite(listing, user)

ListingDep = Annotated[Listing, Depends(get_listing_or_404)]
ListingOwnerDep = Annotated[Listing, Depends(listing_owner_required)]
ListingPublicDep = Annotated[Listing, Depends(get_public_listing_or_404)]
ListingModerateDep = Annotated[Listing, Depends(listing_moderator_required)]
ListingForFavoriteDep = Annotated[Listing, Depends(get_listing_for_favorite)]
