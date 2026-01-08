
from fastapi import APIRouter, status

from app.api.deps import UserDep
from app.schemas import (
    UserDetail,
    UserRatingDetail,
    UserPatch,
    UserPut,
    UserRatingPost,
)
from app.services.user import UserServiceDep

router = APIRouter()

@router.get(
    "/me",
    response_model=UserDetail,
    summary="Получить информацию своего профиля",
)
async def read_users_me(
    user: UserDep,
):
    return user

@router.get(
    "/{id}",
    response_model=UserDetail,
    summary="Получить информацию о пользователе",
)
async def get_user(
    id: int,
    user_service: UserServiceDep,
):
    return await user_service.get_by_id(id)

@router.patch(
    "/me",
    response_model=UserDetail,
    summary="Частичное обновление информации своего пользователя",
)
async def patch_user(
    form_data: UserPatch,
    user: UserDep,
    user_service: UserServiceDep,
):
    return await user_service.update_self(user, form_data)

@router.put(
    "/me",
    response_model=UserDetail,
    summary="Полное обновление информации своего пользователя",
)
async def put_user(
    form_data: UserPut,
    user: UserDep,
    user_service: UserServiceDep
):
    return await user_service.update_self(user, form_data)

@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление своего пользователя",
)
async def delete_user(
    user: UserDep,
    user_service: UserServiceDep,
):
    return await user_service.deactivate_self(user)

@router.get(
    "/{id}/comments", 
    response_model=list[UserRatingDetail],
    summary="Получить комментарии пользователя",
)
async def get_comments(
    id: int,
    user_service: UserServiceDep,
):
    return await user_service.get_comments(id)

@router.post(
    "/{id}/comments",
    response_model=UserRatingDetail,
    summary="Написать комментарий пользователю",
)
async def create_comment(
    id: int,
    user: UserDep,
    form_data: UserRatingPost,
    user_service: UserServiceDep,
):
    return await user_service.create_comment(id, user, form_data)
