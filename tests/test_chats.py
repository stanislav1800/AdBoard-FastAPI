
from fastapi import BackgroundTasks
import pytest
from unittest.mock import AsyncMock, Mock

from app.services.chat_event import ChatEventHandler, MessageCreatedEvent
from tests.fakes import FakeUser



@pytest.mark.asyncio
async def test_get_my_chats(async_client, auth_headers):
    resp = await async_client.get("/api/v1/chat", headers=auth_headers)
    assert resp.status_code == 200

    data = resp.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_chat_detail_success(async_client, auth_headers, chat):
    resp = await async_client.get(f"/api/v1/chat/{chat.id}", headers=auth_headers)
    assert resp.status_code == 200

    data = resp.json()
    assert data["id"] == chat.id
    assert "participants" in data

@pytest.mark.asyncio
async def test_get_chat_detail_forbidden(async_client, auth3_headers, other_chat):
    resp = await async_client.get(f"/api/v1/chat/{other_chat.id}", headers=auth3_headers)
    assert resp.status_code in (403, 404)

@pytest.mark.asyncio
async def test_create_message_success(
    async_client,
    auth_headers,
    chat,
):
    resp = await async_client.post(
        f"/api/v1/chat/{chat.id}/messages",
        json={"text": "Hello"},
        headers=auth_headers,
    )

    assert resp.status_code == 201

@pytest.mark.asyncio
async def test_create_message_forbidden(async_client, auth_headers, user3):
    payload = {"text": "Hello chat!"}
    resp = await async_client.post(
        f"/api/v1/chat/{user3.id}/messages",
        json=payload,
        headers=auth_headers
    )
    assert resp.status_code in (403, 404)

@pytest.mark.asyncio
async def test_chat_lazy_create(
    async_client,
    auth_headers,
    user2,
    listing,
):
    payload = {"text": "Hi there!"}
    resp = await async_client.post(
        f"/api/v1/chat/{listing.id}/{user2.id}",
        json=payload,
        headers=auth_headers,
    )
    assert resp.status_code == 201

@pytest.mark.asyncio
async def test_get_unread_chats_count(async_client, auth_headers, chat_with_unread_messages):
    resp = await async_client.get("/api/v1/chat/unread", headers=auth_headers)
    assert resp.status_code == 200

    data = resp.json()
    assert "unread_chats_count" in data
    assert isinstance(data["unread_chats_count"], int)

@pytest.mark.asyncio
async def test_chat_requires_auth(async_client):
    resp = await async_client.get("/api/v1/chat")
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_no_email_for_online_user():
    """
    Пользователь ONLINE → email НЕ должен добавляться
    """

    sender = FakeUser(id=1)
    receiver = FakeUser(id=2, email="r@test.com")

    chat_repo = AsyncMock()
    chat_repo.get_chat_participants.return_value = [sender, receiver]

    ws_service = Mock()
    ws_service.chat_message = AsyncMock()
    ws_service.chat_list_update = AsyncMock()
    ws_service.unread_update = AsyncMock()
    ws_service.is_user_offline = Mock(return_value=False)

    email_service = Mock()
    email_service.send = Mock()

    handler = ChatEventHandler(
        chat_repo=chat_repo,
        ws_service=ws_service,
        email_service=email_service,
    )

    event = MessageCreatedEvent(
        chat_id=1,
        sender_id=1,
        text="hi",
    )

    bg = BackgroundTasks()

    await handler.handle_message_created(event, bg)

    ws_service.chat_message.assert_awaited()
    ws_service.chat_list_update.assert_awaited()
    ws_service.unread_update.assert_awaited()

    assert len(bg.tasks) == 0


@pytest.mark.asyncio
async def test_email_for_offline_user():
    """
    Пользователь OFFLINE → email ДОЛЖЕН добавиться
    """

    sender = FakeUser(id=1)
    receiver = FakeUser(id=2, email="r@test.com")

    chat_repo = AsyncMock()
    chat_repo.get_chat_participants.return_value = [sender, receiver]

    ws_service = Mock()
    ws_service.chat_message = AsyncMock()
    ws_service.chat_list_update = AsyncMock()
    ws_service.unread_update = AsyncMock()
    ws_service.is_user_offline = Mock(return_value=True)

    email_service = Mock()
    email_service.send = Mock()

    handler = ChatEventHandler(
        chat_repo=chat_repo,
        ws_service=ws_service,
        email_service=email_service,
    )

    event = MessageCreatedEvent(
        chat_id=1,
        sender_id=1,
        text="hi",
    )

    bg = BackgroundTasks()

    await handler.handle_message_created(event, bg)

    assert len(bg.tasks) == 1

    task = bg.tasks[0]
    assert task.func is email_service.send
    assert task.kwargs["recipients"] == ["r@test.com"]

@pytest.mark.asyncio
async def test_ws_notifications_for_all_users():
    """
    Проверка WebSocket уведомлений для всех участников чата:
    - chat_message вызывается
    - chat_list_update вызывается для всех кроме отправителя
    - unread_update вызывается для всех кроме отправителя
    """

    sender = FakeUser(id=1)
    receiver1 = FakeUser(id=2)
    receiver2 = FakeUser(id=3)

    chat_repo = AsyncMock()
    chat_repo.get_chat_participants.return_value = [sender, receiver1, receiver2]

    ws_service = Mock()
    ws_service.chat_message = AsyncMock()
    ws_service.chat_list_update = AsyncMock()
    ws_service.unread_update = AsyncMock()
    ws_service.is_user_offline = Mock(return_value=True)

    email_service = Mock()

    handler = ChatEventHandler(
        chat_repo=chat_repo,
        ws_service=ws_service,
        email_service=email_service,
    )

    event = MessageCreatedEvent(
        chat_id=1,
        sender_id=1,
        text="hello ws"
    )

    bg = BackgroundTasks()

    await handler.handle_message_created(event, bg)

    ws_service.chat_message.assert_awaited_once_with(
        1,
        {
            "chat_id": 1,
            "sender_id": 1,
            "text": "hello ws",
        }
    )

    expected_payload_list = {
        "chat_id": 1,
        "last_message": "hello ws",
    }
    expected_unread_payload = {
        "chat_id": 1,
    }

    ws_service.chat_list_update.assert_any_await(receiver1.id, expected_payload_list)
    ws_service.chat_list_update.assert_any_await(receiver2.id, expected_payload_list)
    ws_service.unread_update.assert_any_await(receiver1.id, expected_unread_payload)
    ws_service.unread_update.assert_any_await(receiver2.id, expected_unread_payload)

    for call_args in ws_service.chat_list_update.await_args_list:
        assert call_args.args[0] != sender.id
    for call_args in ws_service.unread_update.await_args_list:
        assert call_args.args[0] != sender.id
