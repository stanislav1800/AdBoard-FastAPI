import logging

from app.ws.manager import ConnectionManager
from app.ws.presence import PresenceService

logger = logging.getLogger(__name__)


def chat_topic(chat_id: int) -> str:
    return f"chat:{chat_id}"

def user_topic(user_id: int) -> str:
    return f"user:{user_id}"


class WSEventService:
    """
    Единая точка публикации WS-событий
    """
    def __init__(self, manager: ConnectionManager, presence: PresenceService):
        self.manager = manager
        self.presence = presence

    async def chat_message(self, chat_id: int, payload: dict):
        await self.manager.publish(chat_topic(chat_id), {
            "type": "new_message",
            **payload,
        })

    async def typing(self, chat_id: int, user_id: int):
        await self.manager.publish(chat_topic(chat_id), {
            "type": "typing",
            "chat_id": chat_id,
            "user_id": user_id,
        })

    async def chat_list_update(self, user_id: int, payload: dict):
        await self.manager.publish(user_topic(user_id), {
            "type": "chat_list_update",
            **payload,
        })

    async def unread_update(self, user_id: int, payload: dict):
        await self.manager.publish(user_topic(user_id), {
            "type": "unread_count",
            **payload,
        })

    async def is_user_online(self, user_id: int) -> bool:
        try:
            return await self.presence.is_online(user_id)
        except Exception:
            logger.exception("Не удалось получить онлайн-статус пользователя %s", user_id)
            return False

    async def is_user_offline(self, user_id: int) -> bool:
        return not await self.is_user_online(user_id)
