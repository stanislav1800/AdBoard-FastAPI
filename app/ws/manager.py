import asyncio
import json

from fastapi import WebSocket, WebSocketDisconnect

from app.core.config import settings

class ConnectionManager:
    """
    Универсальный менеджер подписок по топикам.
    Никакой бизнес-логики.
    """

    def __init__(self):
        # topic -> set[WebSocket]
        self._topics: dict[str, set[WebSocket]] = {}

    def connect(self, websocket: WebSocket, topic: str):
        self._topics.setdefault(topic, set()).add(websocket)

    def disconnect(self, websocket: WebSocket, topic: str):
        connections = self._topics.get(topic)
        if not connections:
            return

        connections.discard(websocket)
        if not connections:
            self._topics.pop(topic, None)
    
    def disconnect_all(self, websocket: WebSocket):
        for topic in list(self._topics.keys()):
            self.disconnect(websocket, topic)

    async def publish(self, topic: str, message: dict):
        for ws in list(self._topics.get(topic, set())):
            try:
                await ws.send_json(message)
            except WebSocketDisconnect:
                self.disconnect(ws, topic)

    def is_topic_active(self, topic: str) -> bool:
        return bool(self._topics.get(topic))

    def is_user_online(self, user_id: int) -> bool:
        return self.is_topic_active(f"unread:{user_id}")

manager = ConnectionManager()
