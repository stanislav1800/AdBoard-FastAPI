from dataclasses import dataclass
from html import escape
from typing import Annotated

from fastapi import BackgroundTasks, Depends

from app.repositories import ChatRepository, ChatRepositoryDep
from app.services.email import EmailService
from app.ws.chat import WSEventService, ws_service

@dataclass
class MessageCreatedEvent:
    chat_id: int
    sender_id: int
    text: str

class ChatEventHandler:
    def __init__(
        self,
        chat_repo: ChatRepository,
        email_service: EmailService,
        ws_service: WSEventService,
    ):
        self.chat_repo = chat_repo
        self.email_service = email_service
        self.ws_service = ws_service

    async def handle_message_created(self, event: MessageCreatedEvent, background_tasks: BackgroundTasks):
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

            if self.ws_service.is_user_offline(user.id) and user.email:
                subject = f"Новое сообщение в чате #{event.chat_id}"
                body = f"Вы получили новое сообщение:<br><br>{escape(event.text)}"
                background_tasks.add_task(
                    self.email_service.send,
                    recipients=[user.email],
                    subject=subject,
                    body=body,
                )

def get_chat_event(
    chat_repo: ChatRepositoryDep,
) -> ChatEventHandler:
    return ChatEventHandler(
        chat_repo=chat_repo,
        email_service=EmailService(),
        ws_service=ws_service,
    )

ChatEventHandlerDep = Annotated[ChatEventHandler, Depends(get_chat_event)]