
from fastapi import APIRouter, status, BackgroundTasks

from app.schemas import ChatDetail, MessageCreateAPI
from app.services.chat import ChatServiceDep
from app.api.deps import UserDep
from app.services.chat_event import ChatEventHandlerDep

router = APIRouter()

@router.get(
    "/unread",
    summary="Количество непрочитанных чатов",
)
async def get_unread(
    user: UserDep,
    chat_service: ChatServiceDep
):
    count = await chat_service.get_unread_count(user.id)
    return {"unread_chats_count": count}

@router.get(
    "",
    response_model=list[ChatDetail],
    summary="Доступные чаты",
)
async def get_my_chat(
    user: UserDep,
    chat_service: ChatServiceDep
):
    return await chat_service.get_user_chats(user.id)

@router.post(
    "/{id}/messages",
    status_code=status.HTTP_201_CREATED,
    summary="Отправка сообщения в чат",
)
async def create_message(
    id: int,
    form_data: MessageCreateAPI,
    user: UserDep,
    service: ChatServiceDep,
    event_handler: ChatEventHandlerDep,
    background_tasks: BackgroundTasks,
):
    event = await service.create_message(
        chat_id=id,
        sender_id=user.id,
        text=form_data.text,
    )
    await event_handler.handle_message_created(event, background_tasks)

@router.get(
    "/{id}",
    response_model=ChatDetail,
    summary="Получаем чат",
)
async def get_chat(
    id: int,
    user: UserDep,
    chat_service: ChatServiceDep
):
    return await chat_service.ensure_user_can_access(id, user)

@router.post(
    "/{listing_id}/{seller_id}",
    status_code=status.HTTP_201_CREATED,
    summary="Создаем чат и отправляем сообщение",
)
async def chat_lazy_create(
    listing_id: int,
    seller_id: int,
    form_data: MessageCreateAPI,
    user: UserDep,
    chat_service: ChatServiceDep,
    event_handler: ChatEventHandlerDep,
    background_tasks: BackgroundTasks,
):
    event = await chat_service.lazy_create_chat_with_message(
        user_id=user.id,
        seller_id=seller_id,
        listing_id=listing_id,
        text=form_data.text,
    )
    await event_handler.handle_message_created(event, background_tasks)
