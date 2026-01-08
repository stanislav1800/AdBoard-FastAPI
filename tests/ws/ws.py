
# from fastapi.testclient import TestClient
# from fastapi import FastAPI
# import pytest
# from asgi_lifespan import LifespanManager

# from app.main import app
# from app.repositories import UserRepositoryDep
# from app.services.auth import create_access_token
# from app.api.v1.ws import chat as chat_ws_router
# from httpx import AsyncClient, ASGITransport
# from fastapi.websockets import WebSocketDisconnect

# from app.services.chat import ChatService
# from app.services.dependencies import get_current_user_ws
# from app.ws import manager

# async def fake_get_user_repo():
#     class FakeManager:
#         def connect(self, ws, topic): pass
#         def disconnect(self, ws, topic): pass
#         async def publish(self, topic, message): pass

# class FakeMessageRepo:
#     async def create(self, data):
#         # просто возвращаем data как заглушку
#         return data

# class FakeChatRepo:
#     def __init__(self, participants=None):
#         self._participants = participants or []

#     async def get_chat_participants(self, chat_id):
#         # возвращаем заранее заданный список участников
#         return self._participants

# class FakeManager:
#     def __init__(self):
#         self.ws = None

#     def connect(self, ws, topic):
#         self.ws = ws

#     def disconnect(self, ws, topic):
#         self.ws = None

#     async def publish(self, topic, message):
#         await self.ws.send_json(message)

# class FakeUser:
#     def __init__(self, id, chats):
#         self.id = id
#         self.chats = chats
# # @pytest.fixture
# # def app():
# #     app = FastAPI()
# #     # подключаем все роутеры, которые нужны для WS
# #     app.include_router(chat_ws_router.router, prefix="/api/v1/ws")
# #     # app.include_router(auth_router, prefix="/api/v1/auth")
# #     return app


# def test_ws_chat_can_connect_and_receive(monkeypatch, chat, user, override_get_session):
#     # fake manager чтобы publish миррорил сообщения
    
#     class FakeUser:
#         def __init__(self, id, chats):
#             self.id = id
#             self.chats = chats
    
#     async def fake_get_current_user_ws(ws, db, token):
#         return FakeUser(
#             id=user.id,
#             chats=[chat.id],
#         )


#     # monkeypatch.setattr("app.ws.manager.manager", FakeManager())
#     monkeypatch.setattr("app.api.v1.ws.chat.get_current_user_ws", fake_get_current_user_ws)


#     token = create_access_token({"sub": str(user.id)})

#     client = TestClient(app)
#     # подключаемся с токеном как query
#     # async with LifespanManager(app):
#     #     async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
#     with client.websocket_connect(f"/api/v1/ws/chat/{chat.id}?token={token}") as ws:
#         ws.send_text("hello!")
#         pass
#         # data = ws.receive_json()
#         # assert data["type"] == "new_message"
#         # assert data["text"] == "hello!"

# @pytest.mark.asyncio
# async def test_create_message_publishes_ws(monkeypatch):
#     published = []

#     async def fake_publish(topic, payload):
#         published.append((topic, payload))

#     monkeypatch.setattr("app.ws.manager.manager.publish", fake_publish)

#     service = ChatService(
#         message_repo=FakeMessageRepo(),
#         chat_repo=FakeChatRepo(participants=[1, 2]),
#     )

#     await service.create_message(chat_id=1, sender_id=1, text="hello")

#     assert ("chat:1", {"type": "new_message", "chat_id": 1, "sender_id": 1, "text": "hello"}) in published

# def test_ws_chat_connect(monkeypatch):

#     async def fake_get_user(ws, db, token):
#         return FakeUser(id=1, chats=[1])

#     connected = []

#     class FakeManager:
#         def connect(self, ws, topic):
#             connected.append(topic)
#         def disconnect(self, ws, topic): pass

#     monkeypatch.setattr(
#         "app.api.v1.ws.chat.get_current_user_ws",
#         fake_get_user
#     )
#     monkeypatch.setattr(
#         "app.ws.manager.manager",
#         FakeManager()
#     )

#     client = TestClient(app)

#     with client.websocket_connect("/api/v1/ws/chat/1?token=x"):
#         pass

#     assert connected == ["chat:1"]

# # Мокаем get_current_user_ws
# async def fake_get_current_user_ws(ws, db, token):
#     return FakeUser(id=1, chats=[1])

# @pytest.fixture
# def client(monkeypatch):
#     # Мокаем зависимости
#     monkeypatch.setattr("app.ws.manager.manager", FakeManager())
#     monkeypatch.setattr("app.api.v1.ws.chat.get_current_user_ws", fake_get_current_user_ws)
#     return TestClient(app)

# def test_ws_chat_connect_and_receive(client):
#     with client.websocket_connect("/api/v1/ws/chat/1?token=fake") as ws:
#         try:
#             ws.send_text("hello")
#             # проверяем, что сообщение можно отправить и получить
#             # если эндпоинт эхо, можно проверить:
#             # data = ws.receive_text()
#         except Exception:
#             pytest.fail("WebSocket не подключен")

import pytest
from fastapi.testclient import TestClient
from app.services.chat import ChatService

class FakeMessageRepo:
    async def create(self, data):
        return {"chat_id": data.chat_id, "sender_id": data.sender_id, "text": data.text}

class FakeChatRepo:
    def __init__(self, participants=None):
        self._participants = participants or []

    async def get_chat_participants(self, chat_id):
        return self._participants

# ---------------------------
# ws_chat: connect/disconnect
# ---------------------------
def test_ws_chat_connect_and_disconnect(client, patch_ws):
    fake_user, fake_manager = patch_ws
    with client.websocket_connect("/api/v1/ws/chat/1?token=fake"):
        pass
    assert "chat:1" in fake_manager.connected

# ---------------------------
# ws_chat_list: connect/disconnect
# ---------------------------
def test_ws_chat_list_connect_and_disconnect(client, patch_ws):
    fake_user, fake_manager = patch_ws
    with client.websocket_connect("/api/v1/ws/chat-list?token=fake"):
        pass
    assert f"chat_list:{fake_user.id}" in fake_manager.connected

# ---------------------------
# ws_unread: connect/publish
# ---------------------------
def test_ws_unread_connect_and_publish(client, patch_ws):
    fake_user, fake_manager = patch_ws
    import asyncio
    with client.websocket_connect("/api/v1/ws/unread?token=fake"):
        asyncio.run(fake_manager.publish(f"unread:{fake_user.id}", {"test": 1}))
    assert f"unread:{fake_user.id}" in [t for t, _ in fake_manager.published]

# ---------------------------
# ws_typing: connect/disconnect
# ---------------------------
def test_ws_typing_connect_and_disconnect(client, patch_ws):
    fake_user, fake_manager = patch_ws
    with client.websocket_connect("/api/v1/ws/typing/1?token=fake"):
        pass
    assert "typing:1" in fake_manager.connected

# ---------------------------
# Триггер publish через create_message → unit
# ---------------------------
@pytest.mark.asyncio
async def test_create_message_triggers_ws(patch_ws):
    fake_user, fake_manager = patch_ws
    service = ChatService(
        message_repo=FakeMessageRepo(),
        chat_repo=FakeChatRepo(participants=[1, 2]),
    )
    await service.create_message(chat_id=1, sender_id=1, text="hello")
    assert ("chat:1", {"type": "new_message", "chat_id": 1, "sender_id": 1, "text": "hello"}) in fake_manager.published


# ---------------------------
# Интеграционный FakeManager
# ---------------------------
class IntegrationFakeManager:
    def __init__(self):
        self.connected = []
        self.disconnected = []
        self.published = []

    def connect(self, ws, topic):
        self.connected.append(topic)

    def disconnect(self, ws, topic):
        self.disconnected.append(topic)

    async def publish(self, topic, payload):
        self.published.append((topic, payload))

# ---------------------------
# Фейковый get_current_user_ws
# ---------------------------
async def fake_get_user(ws, db, token=None):
    class FakeUser:
        id = 1
        chats = [1]
    return FakeUser()

# ---------------------------
# Фикстуры
# ---------------------------
@pytest.fixture
def fake_manager(monkeypatch):
    fake = IntegrationFakeManager()
    monkeypatch.setattr("app.ws.manager.manager", fake)
    return fake

@pytest.fixture
def fake_get_user_monkey(monkeypatch):
    monkeypatch.setattr("app.api.v1.ws.chat.get_current_user_ws", fake_get_user)

@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)

# ---------------------------
# Интеграционные тесты WS
# ---------------------------

def test_ws_chat_full_cycle(client, fake_manager, fake_get_user_monkey):
    with client.websocket_connect("/api/v1/ws/chat/1?token=fake") as ws:
        # отправляем сообщение
        ws.send_text("hello world")
    
    # проверяем подключение и отключение
    assert "chat:1" in fake_manager.connected
    assert "chat:1" in fake_manager.disconnected

def test_ws_chat_list_full_cycle(client, fake_manager, fake_get_user_monkey):
    with client.websocket_connect("/api/v1/ws/chat-list"):
        pass
    assert "chat_list:1" in fake_manager.connected
    assert "chat_list:1" in fake_manager.disconnected

def test_ws_unread_full_cycle(client, fake_manager, fake_get_user_monkey):
    with client.websocket_connect("/api/v1/ws/unread") as ws:
        ws.send_text('{"chat_id":1}')
    
    assert "unread:1" in fake_manager.connected
    assert fake_manager.published
    topic, payload = fake_manager.published[0]
    assert topic == "unread:1"
    assert payload == '{"chat_id":1}'

def test_ws_typing_full_cycle(client, fake_manager, fake_get_user_monkey):
    with client.websocket_connect("/api/v1/ws/typing/1") as ws:
        ws.send_text("typing...")
    
    assert "typing:1" in fake_manager.connected
    assert "typing:1" in fake_manager.disconnected

@pytest.mark.asyncio
async def test_create_message_triggers_ws(client, fake_manager, fake_get_user_monkey):
    from app.services.chat import ChatService
    # фейковые репозитории
    class FakeMessageRepo:
        async def create(self, data): return data

    class FakeChatRepo:
        async def get_chat_participants(self, chat_id): return [1, 2]

    service = ChatService(message_repo=FakeMessageRepo(), chat_repo=FakeChatRepo())

    await service.create_message(chat_id=1, sender_id=1, text="hello")

    topics = [t for t, _ in fake_manager.published]
    assert "chat:1" in topics
    assert "chat_list:2" in topics
    assert "unread:2" in topics