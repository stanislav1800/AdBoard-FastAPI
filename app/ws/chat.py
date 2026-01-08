
from app.ws.manager import ConnectionManager, manager

class WSEventService:
    """
    Единая точка публикации WS-событий
    """
    def __init__(self, manager: ConnectionManager):
        self.manager = manager

    async def chat_message(self, chat_id: int, payload: dict):
        await self.manager.publish(f"chat:{chat_id}", {
            "type": "new_message",
            **payload,
        })

    async def chat_list_update(self, user_id: int, payload: dict):
        await self.manager.publish(f"chat_list:{user_id}", {
            "type": "chat_list_update",
            **payload,
        })

    async def unread_update(self, user_id: int, payload: dict):
        await self.manager.publish(f"unread:{user_id}", {
            "type": "unread_count",
            **payload,
        })

    def is_user_online(self, user_id: int) -> bool:
        return self.manager.is_topic_active(f"unread:{user_id}")

    def is_user_offline(self, user_id: int) -> bool:
        return not self.is_user_online(user_id)

ws_service = WSEventService(manager=manager)
