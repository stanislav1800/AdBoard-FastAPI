from typing import Annotated

from fastapi import Depends

from .base import get_repository
from .user import UserRepository
from .user_rating import UserRatingRepository
from .listing import ListingRepository
from .listing_favorites import ListingFavoriteRepository
from .listing_image import ListingImageRepository
from .category import CategoryRepository
from .chat import ChatRepository
from .message import MessageRepository
from .moderation import ModerationLogRepository

UserRepositoryDep = Annotated[UserRepository, Depends(get_repository(UserRepository))]
UserRatingRepositoryDep = Annotated[UserRatingRepository, Depends(get_repository(UserRatingRepository))]
ListingRepositoryDep = Annotated[ListingRepository, Depends(get_repository(ListingRepository))]
ListingFavoriteRepositoryDep = Annotated[ListingFavoriteRepository, Depends(get_repository(ListingFavoriteRepository))]
ListingImageRepositoryDep = Annotated[ListingImageRepository, Depends(get_repository(ListingImageRepository))]
CategoryRepositoryDep = Annotated[CategoryRepository, Depends(get_repository(CategoryRepository))]
ChatRepositoryDep = Annotated[ChatRepository, Depends(get_repository(ChatRepository))]
MessageRepositoryDep = Annotated[MessageRepository, Depends(get_repository(MessageRepository))]
ModerationLogRepositoryDep = Annotated[ModerationLogRepository, Depends(get_repository(ModerationLogRepository))]

__all__ = [
    "UserRepositoryDep",
    "UserRatingRepositoryDep",
    "ListingRepositoryDep",
    "ListingFavoriteRepositoryDep",
    "ListingImageRepositoryDep",
    "CategoryRepositoryDep",
    "ChatRepositoryDep",
    "MessageRepositoryDep",
    "ModerationLogRepositoryDep",
]
