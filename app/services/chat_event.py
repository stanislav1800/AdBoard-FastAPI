from dataclasses import dataclass
from html import escape
from typing import Annotated

from fastapi import Depends

from app.repositories import ChatRepository, ChatRepositoryDep
from app.tasks.email import EmailQueue, get_email_queue
from app.ws.chat import WSEventService
from app.ws.runtime import WSEventServiceDep

@dataclass
class MessageCreatedEvent:
    chat_id: int
    sender_id: int
    text: str

class ChatEventHandler:
    def __init__(
        self,
        chat_repo: ChatRepository,
        email_queue: EmailQueue,
        ws_service: WSEventService,
    ):
        self.chat_repo = chat_repo
        self.email_queue = email_queue
        self.ws_service = ws_service

    async def handle_message_created(self, event: MessageCreatedEvent):
        participants = await self.chat_repo.get_chat_participants(event.chat_id)
        await self.ws_service.chat_message(event.chat_id, {
            "chat_id": event.chat_id,
            "sender_id": event.sender_id,
            "text": event.text,
        })

        for user in participants:
            if user.id == event.sender_id:
                continue

            await self.ws_service.chat_list_update(user.id, {
                "chat_id": event.chat_id,
                "last_message": event.text,
            })

            await self.ws_service.unread_update(user.id, {
                "chat_id": event.chat_id,
            })

            if user.email and await self.ws_service.is_user_offline(user.id):
                subject = f"Новое сообщение в чате #{event.chat_id}"
                body = f"Вы получили новое сообщение:<br><br>{escape(event.text)}"
                await self.email_queue.send(
                    recipients=[user.email],
                    subject=subject,
                    body=body,
                )

def get_chat_event(
    chat_repo: ChatRepositoryDep,
    ws_service: WSEventServiceDep,
    email_queue: Annotated[EmailQueue, Depends(get_email_queue)],
) -> ChatEventHandler:
    return ChatEventHandler(
        chat_repo=chat_repo,
        email_queue=email_queue,
        ws_service=ws_service,
    )

ChatEventHandlerDep = Annotated[ChatEventHandler, Depends(get_chat_event)]