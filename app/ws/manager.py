import asyncio
import logging

from fastapi import WebSocket

from app.ws.broker import PubSubBroker

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Локальный реестр подписок сокетов этого воркера по топикам.
    Публикация идёт через брокер, поэтому событие доходит до сокетов на всех воркерах.
    Никакой бизнес-логики.
    """

    def __init__(self, broker: PubSubBroker, send_timeout: float = 5.0):
        self._broker = broker
        self._send_timeout = send_timeout
        self._topics: dict[str, set[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def start(self):
        await self._broker.start(self._deliver)

    async def stop(self):
        await self._broker.stop()

    async def subscribe(self, websocket: WebSocket, topic: str):
        async with self._lock:
            connections = self._topics.get(topic)
            if connections is None:
                await self._broker.subscribe(topic)
                connections = self._topics[topic] = set()
            connections.add(websocket)

    async def unsubscribe(self, websocket: WebSocket, topic: str):
        async with self._lock:
            connections = self._topics.get(topic)
            if not connections or websocket not in connections:
                return

            connections.discard(websocket)
            if not connections:
                del self._topics[topic]
                await self._broker.unsubscribe(topic)

    async def unsubscribe_all(self, websocket: WebSocket):
        topics = [topic for topic, connections in self._topics.items() if websocket in connections]
        for topic in topics:
            await self.unsubscribe(websocket, topic)

    async def publish(self, topic: str, message: dict):
        try:
            await self._broker.publish(topic, message)
        except Exception:
            logger.exception("Не удалось опубликовать WS-событие в топик %s", topic)

    def is_topic_active(self, topic: str) -> bool:
        return bool(self._topics.get(topic))

    async def _deliver(self, topic: str, message: dict):
        """Доставка события из брокера локальным сокетам"""
        connections = list(self._topics.get(topic, ()))
        if not connections:
            return

        results = await asyncio.gather(*(self._send(ws, message) for ws in connections))
        for ws, ok in zip(connections, results):
            if not ok:
                await self._drop(ws)

    async def _send(self, websocket: WebSocket, message: dict) -> bool:
        try:
            await asyncio.wait_for(websocket.send_json(message), self._send_timeout)
            return True
        except Exception:
            return False

    async def _drop(self, websocket: WebSocket):
        """Мёртвый или зависший сокет: отписываем и закрываем"""
        await self.unsubscribe_all(websocket)
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
