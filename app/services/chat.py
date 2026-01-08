import logging
from typing import Annotated

from fastapi import Depends

from app.core.exceptions import ChatNotFoundException, UserNotAccessException
from app.models.user import User
from app.repositories import ChatRepositoryDep, MessageRepositoryDep
from app.repositories.chat import ChatRepository
from app.repositories.message import MessageRepository
from app.schemas.message import MessageDBCreate
from app.services.chat_event import MessageCreatedEvent

logger = logging.getLogger()

class ChatService:
    def __init__(self, message_repo: MessageRepository, chat_repo: ChatRepository):
        self.message_repo = message_repo
        self.chat_repo = chat_repo

    async def create_message(self,
        chat_id: int,
        sender_id: int,
        text: str,
    ):
        chat = await self.get_or_404(chat_id)
        if sender_id not in {u.id for u in chat.participants}:
            raise UserNotAccessException
        
        message = await self.message_repo.create(
            MessageDBCreate(
                chat_id=chat_id,
                sender_id=sender_id,
                text=text,
            )
        )
        return MessageCreatedEvent(
            chat_id=chat_id,
            sender_id=sender_id,
            text=text,
        )
    
    async def lazy_create_chat_with_message(
        self,
        user_id: int,
        seller_id: int,
        listing_id: int,
        text: str,
    ):
        chat = await self.chat_repo.chat_lazy_create(user_id, seller_id, listing_id)
        await self.message_repo.create(MessageDBCreate(chat_id=chat.id, sender_id=user_id, text=text))

        return MessageCreatedEvent(
            chat_id=chat.id,
            sender_id=user_id,
            text=text,
        )
    
    async def get_or_404(self, chat_id: int):
        chat = await self.chat_repo.get_by_id(chat_id)
        if not chat:
            raise ChatNotFoundException
        return chat

    async def ensure_user_can_access(self, chat_id: int, user: User):
        chat = await self.get_or_404(chat_id)
        if user not in chat.participants:
            raise UserNotAccessException
        return chat
    
    async def get_unread_count(self, user_id: int) -> int:
        return await self.chat_repo.get_unread(user_id)

    async def get_user_chats(self, user_id: int):
        return await self.chat_repo.get_chats(user_id)

def get_chat_service(
    message_repo: MessageRepositoryDep,
    chat_repo: ChatRepositoryDep,
) -> ChatService:
    return ChatService(message_repo, chat_repo)

ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
