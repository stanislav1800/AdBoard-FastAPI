import asyncio
import logging
import uuid

import jwt
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from app.core.database import SessionFactory
from app.models import User
from app.repositories import ChatRepository, UserRepository
from app.schemas.ws import WSClientMessage
from app.services.auth import AuthService
from app.ws.chat import chat_topic, user_topic
from app.ws.runtime import WSRuntime

logger = logging.getLogger(__name__)


async def authenticate_ws(session_factory: SessionFactory, token: str | None) -> User | None:
    if not token:
        return None
    async with session_factory() as session:
        try:
            return await AuthService(UserRepository(session)).get_user_from_token(token)
        except jwt.PyJWTError:
            return None


class ChatSocketHandler:

    def __init__(
        self,
        websocket: WebSocket,
        user: User,
        runtime: WSRuntime,
        session_factory: SessionFactory,
    ):
        self.ws = websocket
        self.user_id = user.id
        self.runtime = runtime
        self.session_factory = session_factory
        self.connection_id = uuid.uuid4().hex
        self.chats: set[int] = set()

    async def run(self):
        await self.ws.accept()
        manager, presence = self.runtime.manager, self.runtime.presence

        await manager.subscribe(self.ws, user_topic(self.user_id))
        await presence.touch(self.user_id, self.connection_id)
        heartbeat = asyncio.create_task(self._heartbeat())
        try:
            while True:
                await self._handle(await self.ws.receive_text())
        except WebSocketDisconnect:
            pass
        finally:
            heartbeat.cancel()
            await manager.unsubscribe_all(self.ws)
            await presence.disconnect(self.user_id, self.connection_id)

    async def _heartbeat(self):
        interval = self.runtime.presence.ttl / 3
        while True:
            await asyncio.sleep(interval)
            try:
                await self.runtime.presence.touch(self.user_id, self.connection_id)
            except Exception:
                logger.exception("Не удалось продлить онлайн-статус пользователя %s", self.user_id)

    async def _handle(self, raw: str):
        try:
            msg = WSClientMessage.model_validate_json(raw)
        except ValidationError:
            await self._error("Некорректное сообщение")
            return

        if msg.action == "ping":
            await self.ws.send_json({"type": "pong"})
            return

        if msg.chat_id is None:
            await self._error("chat_id обязателен", msg.action)
            return

        if msg.action == "subscribe":
            await self._subscribe(msg.chat_id)
        elif msg.action == "unsubscribe":
            await self._unsubscribe(msg.chat_id)
        elif msg.action == "typing":
            await self._typing(msg.chat_id)

    async def _subscribe(self, chat_id: int):
        async with self.session_factory() as session:
            allowed = await ChatRepository(session).user_can_write(chat_id, self.user_id)
        if not allowed:
            await self._error("Чат не найден или нет доступа", "subscribe", chat_id)
            return

        await self.runtime.manager.subscribe(self.ws, chat_topic(chat_id))
        self.chats.add(chat_id)
        await self.ws.send_json({"type": "subscribed", "chat_id": chat_id})

    async def _unsubscribe(self, chat_id: int):
        await self.runtime.manager.unsubscribe(self.ws, chat_topic(chat_id))
        self.chats.discard(chat_id)
        await self.ws.send_json({"type": "unsubscribed", "chat_id": chat_id})

    async def _typing(self, chat_id: int):
        if chat_id not in self.chats:
            await self._error("Сначала подпишитесь на чат", "typing", chat_id)
            return
        await self.runtime.events.typing(chat_id, self.user_id)

    async def _error(self, detail: str, action: str | None = None, chat_id: int | None = None):
        await self.ws.send_json({
            "type": "error",
            "action": action,
            "chat_id": chat_id,
            "detail": detail,
        })
