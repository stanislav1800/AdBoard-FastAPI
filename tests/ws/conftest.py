# conftest.py
import pytest
from fastapi.testclient import TestClient
from app.main import app
from types import SimpleNamespace

# ---- Fake components ----
class FakeUser:
    def __init__(self, id: int, chats=None):
        self.id = id
        self.chats = chats or []

class FakeManager:
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

@pytest.fixture
def fake_user():
    return FakeUser(id=1, chats=[1])

@pytest.fixture
def fake_manager():
    return FakeManager()

@pytest.fixture
def client():
    return TestClient(app)

# ---- Patch WS dependencies ----
@pytest.fixture
def patch_ws(monkeypatch, fake_user, fake_manager):
    # Патчим manager и get_current_user_ws прямо в модуле WS
    import app.ws.router as ws_module

    monkeypatch.setattr(ws_module, "manager", fake_manager)

    async def fake_get_current_user_ws(ws, db, token=None):
        return fake_user

    monkeypatch.setattr(ws_module, "get_current_user_ws", fake_get_current_user_ws)

    # Патчим WSEventBus внутри ws_module
    class FakeWSEventBus:
        @staticmethod
        async def chat_message(chat_id, payload):
            await fake_manager.publish(f"chat:{chat_id}", payload)

        @staticmethod
        async def chat_list_update(user_id, payload):
            await fake_manager.publish(f"chat_list:{user_id}", payload)

        @staticmethod
        async def unread_update(user_id, payload):
            await fake_manager.publish(f"unread:{user_id}", payload)

    monkeypatch.setattr(ws_module, "WSEventBus", FakeWSEventBus)
    return fake_user, fake_manager
