from typing import Annotated

from fastapi import Depends

from app.core.exceptions import UserNotFoundException, UserNotCommentYourselfException
from app.models import User
from app.repositories import UserRatingRepositoryDep, UserRepositoryDep, UserRepository, UserRatingRepository
from app.schemas import UserUpdateAdmin, UserRatingCreate, UserRatingDetail, UserRatingPost

class UserService:
    def __init__(
        self,
        user_repo: UserRepository,
        rating_repo: UserRatingRepository,
    ):
        self.user_repo = user_repo
        self.rating_repo = rating_repo

    async def get_by_id(self, id: int) -> User:
        user = await self.user_repo.get_by_id(id)
        if not user:
            raise UserNotFoundException
        return user

    async def update_self(
        self,
        user: User,
        data,
    ) -> User:
        return await self.user_repo.update(user, data, exclude_unset=True)

    async def deactivate_self(self, user: User):
        data = UserUpdateAdmin(is_active=False)
        await self.user_repo.update(user, data, exclude_unset=True)

    async def get_comments(self, user_id: int):
        return await self.rating_repo.get_by_filters(user_id=user_id)

    async def create_comment(
        self,
        target_user_id: int,
        author: User,
        data: UserRatingPost,
    ) -> UserRatingDetail:
        if target_user_id == author.id:
            raise UserNotCommentYourselfException

        return await self.rating_repo.create(UserRatingCreate(
            score=data.score,
            comment=data.comment,
            user_id=target_user_id,
            rater_id=author.id,
        ))

def get_user_service(
    user_repo: UserRepositoryDep,
    rating_repo: UserRatingRepositoryDep,
) -> UserService:
    return UserService(user_repo=user_repo, rating_repo=rating_repo)

UserServiceDep = Annotated[UserService, Depends(get_user_service)]
