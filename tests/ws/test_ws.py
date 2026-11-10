import asyncio
from unittest.mock import AsyncMock

import pytest

from httpx_ws import WebSocketDisconnect

from app.core.security import create_refresh_token

RECEIVE_TIMEOUT = 2


async def wait_for(condition, timeout: float = 2.0):
    async def _poll():
        while not await condition():
            await asyncio.sleep(0.01)
    await asyncio.wait_for(_poll(), timeout)


async def assert_rejected(ws_connect, token: str):
    """Соединение отклонено с кодом 1008 (policy violation)"""
    with pytest.RaisesGroup(pytest.RaisesExc(WebSocketDisconnect, check=lambda e: e.code == 1008)):
        async with ws_connect(token):
            pass


async def subscribe(ws, chat_id: int) -> dict:
    await ws.send_json({"action": "subscribe", "chat_id": chat_id})
    return await ws.receive_json(timeout=RECEIVE_TIMEOUT)


# ————————————————————————————————
# Авторизация
# ————————————————————————————————

@pytest.mark.asyncio
@pytest.mark.parametrize("token", ["", "invalidtoken"])
async def test_rejects_invalid_token(ws_connect, token):
    await assert_rejected(ws_connect, token)

@pytest.mark.asyncio
async def test_rejects_refresh_token(ws_connect, user):
    token = create_refresh_token({"sub": str(user.id)})
    await assert_rejected(ws_connect, token)

@pytest.mark.asyncio
async def test_ping_pong(ws_connect, user_token):
    async with ws_connect(user_token) as ws:
        await ws.send_json({"action": "ping"})
        assert await ws.receive_json(timeout=RECEIVE_TIMEOUT) == {"type": "pong"}

@pytest.mark.asyncio
async def test_invalid_message(ws_connect, user_token):
    async with ws_connect(user_token) as ws:
        await ws.send_text("not json")
        resp = await ws.receive_json(timeout=RECEIVE_TIMEOUT)
        assert resp["type"] == "error"

        await ws.send_json({"action": "subscribe"})
        resp = await ws.receive_json(timeout=RECEIVE_TIMEOUT)
        assert resp["type"] == "error"

# ————————————————————————————————
# Подписки на чаты
# ————————————————————————————————

@pytest.mark.asyncio
async def test_subscribe_own_chat(ws_connect, user_token, chat):
    async with ws_connect(user_token) as ws:
        assert await subscribe(ws, chat.id) == {"type": "subscribed", "chat_id": chat.id}

        await ws.send_json({"action": "unsubscribe", "chat_id": chat.id})
        resp = await ws.receive_json(timeout=RECEIVE_TIMEOUT)
        assert resp == {"type": "unsubscribed", "chat_id": chat.id}

@pytest.mark.asyncio
async def test_cannot_subscribe_foreign_chat(ws_connect, user3_token, chat):
    async with ws_connect(user3_token) as ws:
        resp = await subscribe(ws, chat.id)
        assert resp["type"] == "error"
        assert resp["chat_id"] == chat.id

@pytest.mark.asyncio
async def test_new_message_delivered(ws_connect, async_client, user_token, auth2_headers, chat, user, user2):
    async with ws_connect(user_token) as ws:
        await subscribe(ws, chat.id)

        resp = await async_client.post(
            f"/api/v1/chat/{chat.id}/messages",
            json={"text": "Hello"},
            headers=auth2_headers,
        )
        assert resp.status_code == 201

        events = [await ws.receive_json(timeout=RECEIVE_TIMEOUT) for _ in range(3)]
        by_type = {e["type"]: e for e in events}

        assert by_type["new_message"] == {
            "type": "new_message",
            "chat_id": chat.id,
            "sender_id": user2.id,
            "text": "Hello",
        }
        assert by_type["chat_list_update"]["last_message"] == "Hello"
        assert by_type["unread_count"]["chat_id"] == chat.id

@pytest.mark.asyncio
async def test_typing(ws_connect, user_token, user2_token, chat, user2):
    async with (
        ws_connect(user_token) as ws1,
        ws_connect(user2_token) as ws2,
    ):
        await subscribe(ws1, chat.id)
        await subscribe(ws2, chat.id)

        await ws2.send_json({"action": "typing", "chat_id": chat.id})

        resp = await ws1.receive_json(timeout=RECEIVE_TIMEOUT)
        assert resp == {"type": "typing", "chat_id": chat.id, "user_id": user2.id}

@pytest.mark.asyncio
async def test_typing_requires_subscription(ws_connect, user_token, chat):
    async with ws_connect(user_token) as ws:
        await ws.send_json({"action": "typing", "chat_id": chat.id})
        resp = await ws.receive_json(timeout=RECEIVE_TIMEOUT)
        assert resp["type"] == "error"

# ————————————————————————————————
# Онлайн-статус и email
# ————————————————————————————————

@pytest.mark.asyncio
async def test_presence(ws_connect, ws_runtime, user, user_token):
    presence = ws_runtime.presence
    assert not await presence.is_online(user.id)

    async with ws_connect(user_token) as ws:
        await ws.send_json({"action": "ping"})
        await ws.receive_json(timeout=RECEIVE_TIMEOUT)
        assert await presence.is_online(user.id)

    async def offline():
        return not await presence.is_online(user.id)
    await wait_for(offline)

@pytest.mark.asyncio
@pytest.mark.parametrize("online, emails_sent", [(True, 0), (False, 1)])
async def test_email_only_when_offline(
    monkeypatch, session, ws_connect, async_client,
    user, user_token, auth2_headers, chat,
    online, emails_sent,
):
    user.email = "user@test.com"
    await session.commit()

    send = AsyncMock()
    monkeypatch.setattr("app.services.email.EmailService.send", send)

    async def post_message():
        resp = await async_client.post(
            f"/api/v1/chat/{chat.id}/messages",
            json={"text": "Hello"},
            headers=auth2_headers,
        )
        assert resp.status_code == 201

    if online:
        async with ws_connect(user_token) as ws:
            await ws.send_json({"action": "ping"})
            await ws.receive_json(timeout=RECEIVE_TIMEOUT)
            await post_message()
    else:
        await post_message()

    assert send.await_count == emails_sent
