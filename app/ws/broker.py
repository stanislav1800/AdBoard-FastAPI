import asyncio
import json
import logging
from abc import ABC, abstractmethod
from typing import Awaitable, Callable

from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

logger = logging.getLogger(__name__)

MessageHandler = Callable[[str, dict], Awaitable[None]]


class PubSubBroker(ABC):

    @abstractmethod
    async def start(self, handler: MessageHandler) -> None:
        """Запустить приём сообщений, handler(topic, message) вызывается на каждое"""

    @abstractmethod
    async def stop(self) -> None: ...

    @abstractmethod
    async def publish(self, topic: str, message: dict) -> None: ...

    @abstractmethod
    async def subscribe(self, topic: str) -> None: ...

    @abstractmethod
    async def unsubscribe(self, topic: str) -> None: ...


class RedisPubSubBroker(PubSubBroker):
    CONTROL_CHANNEL = "__control__"

    def __init__(self, redis: Redis, prefix: str = "ws:", reconnect_delay: float = 1.0):
        self._redis = redis
        self._prefix = prefix
        self._reconnect_delay = reconnect_delay
        self._pubsub = None
        self._task: asyncio.Task | None = None
        self._handler: MessageHandler | None = None

    def _channel(self, topic: str) -> str:
        return f"{self._prefix}{topic}"

    async def start(self, handler: MessageHandler) -> None:
        self._handler = handler
        self._pubsub = self._redis.pubsub(ignore_subscribe_messages=True)
        await self._pubsub.subscribe(self._channel(self.CONTROL_CHANNEL))
        self._task = asyncio.create_task(self._listen())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None
        if self._pubsub:
            await self._pubsub.aclose()
            self._pubsub = None

    async def publish(self, topic: str, message: dict) -> None:
        await self._redis.publish(self._channel(topic), json.dumps(message))

    async def subscribe(self, topic: str) -> None:
        await self._pubsub.subscribe(self._channel(topic))

    async def unsubscribe(self, topic: str) -> None:
        await self._pubsub.unsubscribe(self._channel(topic))

    async def _listen(self) -> None:
        while True:
            try:
                message = await self._pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=None
                )
            except RedisConnectionError:
                logger.warning("Redis pub/sub: соединение потеряно, переподключаемся")
                await asyncio.sleep(self._reconnect_delay)
                continue

            if not message or message["type"] != "message":
                continue

            topic = message["channel"].removeprefix(self._prefix)
            try:
                await self._handler(topic, json.loads(message["data"]))
            except Exception:
                logger.exception("Ошибка обработки WS-события из топика %s", topic)
