from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, Mock

from fastapi.testclient import TestClient
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncConnection, async_sessionmaker
from sqlalchemy.pool import NullPool

from app.main import app
from app.core.config import settings
from app.core.database import get_async_session
from app.core.security import create_access_token, get_password_hash
from app.models import Base, User, UserRoleEnum, Chat, Listing, Message


test_async_engine = create_async_engine(settings.get_test_db_url(), echo=False, poolclass=NullPool)
test_async_session = async_sessionmaker(test_async_engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="session", autouse=True)
async def init_db() -> AsyncGenerator[None, None]:
    """
    Создаем таблицы один раз перед всеми тестами.
    После завершения можно опционально удалить таблицы.
    """
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def db_connection() -> AsyncGenerator[AsyncConnection, None]:
    async with test_async_engine.connect() as conn:
        await conn.begin()
        yield conn
        await conn.rollback()

@pytest.fixture(scope="function")
async def session(db_connection: AsyncConnection) -> AsyncGenerator[AsyncSession, None]:
    async_session = AsyncSession(
        bind=db_connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )
    yield async_session
    await async_session.close()

@pytest.fixture
def override_get_session(session):
    async def _override():
        yield session

    app.dependency_overrides[get_async_session] = _override
    yield
    app.dependency_overrides.clear()

# ————————————————————————————————
# 3. HTTP TestClient
# ————————————————————————————————

@pytest.fixture
def test_client(override_get_session):
    """
    Синхронный HTTP клиент.
    TestClient знает, что надо подставить тестовую DB.
    """
    with TestClient(app) as c:
        yield c

# ————————————————————————————————
# 4. Async HTTP клиент (httpx)
# ————————————————————————————————

@pytest.fixture
async def async_client(override_get_session):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as ac:
        yield ac



# ————————————————————————————————
# 5. WebSocket клиент‑фабрика
# ————————————————————————————————

# @pytest_asyncio.fixture
# async def async_client(override_get_session):
#     app.dependency_overrides[get_async_session] = override_get_session
#     async with AsyncClient(
#         transport=ASGITransport(app=app), base_url="https://topok.com"
#     ) as client:
#         yield client
#     app.dependency_overrides.clear()

@pytest_asyncio.fixture
async def websocket_client(async_client):
    async with async_client.websocket_connect("/ws/123") as websocket:
        yield websocket

@pytest.fixture
def ws_connect(test_client):
    """
    Возвращает функцию,
    которая подключается к WebSocket.
    Пример:
        ws = ws_connect_factory("/ws/chat/123")
    """
    def _connect(path: str):
        return test_client.websocket_connect(path)
    return _connect

# ————————————————————————————————
# 6. Fixture клиент‑фабрика
# ————————————————————————————————

@pytest.fixture()
async def user(session):
    user = User(
        username="user",
        password=get_password_hash("user"),
        role=UserRoleEnum.USER,
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@pytest.fixture()
async def user2(session):
    user = User(
        username="user2",
        password=get_password_hash("user2"),
        role=UserRoleEnum.USER,
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@pytest.fixture()
async def user3(session):
    user = User(
        username="user3",
        password=get_password_hash("user3"),
        role=UserRoleEnum.USER,
        is_active=True,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@pytest.fixture()
async def admin(session):
    admin = User(
        username="admin",
        password=get_password_hash("admin"),
        role=UserRoleEnum.ADMIN,
        is_active=True,
    )
    session.add(admin)
    await session.commit()
    await session.refresh(admin)
    return admin

@pytest.fixture()
async def moderator(session):
    moderator = User(
        username="moderator",
        password=get_password_hash("moderator"),
        role=UserRoleEnum.MODERATOR,
        is_active=True,
    )
    session.add(moderator)
    await session.commit()
    await session.refresh(moderator)
    return moderator


@pytest.fixture()
def user_token(user):
    return create_access_token({"sub": str(user.id)})

@pytest.fixture()
def user2_token(user2):
    return create_access_token({"sub": str(user2.id)})

@pytest.fixture()
def user3_token(user3):
    return create_access_token({"sub": str(user3.id)})

@pytest.fixture()
def admin_token(admin):
    return create_access_token({"sub": str(admin.id)})

@pytest.fixture()
def moderator_token(moderator):
    return create_access_token({"sub": str(moderator.id)})


@pytest.fixture()
def auth_headers(user_token):
    return {"Authorization": f"Bearer {user_token}"}

@pytest.fixture
def auth2_headers(user2_token):
    return {"Authorization": f"Bearer {user2_token}"}

@pytest.fixture()
def auth3_headers(user3_token):
    return {"Authorization": f"Bearer {user3_token}"}

@pytest.fixture()
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture()
def moderator_headers(moderator_token):
    return {"Authorization": f"Bearer {moderator_token}"}


@pytest.fixture
async def listing(session, user):
    listing = Listing(title="Listing", description="desc", price=100, condition="new", location="City", user_id=user.id)
    session.add(listing)
    await session.commit()
    await session.refresh(listing)
    return listing

@pytest.fixture
async def other_listing(session, user):
    listing = Listing(title="Listing", description="desc", price=100, condition="new", location="City", user_id=user.id)
    session.add(listing)
    await session.commit()
    await session.refresh(listing)
    return listing

@pytest.fixture
async def chat(session, user, user2, listing):
    chat = Chat(listing_id=listing.id)
    chat.participants.append(user)
    chat.participants.append(user2)
    session.add(chat)
    await session.commit()
    await session.refresh(chat)
    return chat

@pytest.fixture
async def other_chat(session, user, user2, other_listing):
    chat = Chat(listing_id=other_listing.id)
    chat.participants.append(user)
    chat.participants.append(user2)
    session.add(chat)
    await session.commit()
    await session.refresh(chat)
    return chat

@pytest.fixture
async def message(session, chat, user):
    msg = Message(chat_id=chat.id, sender_id=user.id, text="Hello")
    session.add(msg)
    await session.commit()
    await session.refresh(msg)
    return msg

@pytest.fixture
async def chat_with_unread_messages(session: AsyncSession, user, user2, listing):
    """
    Создаём чат с участниками user и other_user,
    добавляем непрочитанное сообщение от user
    """
    chat = Chat(listing_id=listing.id)
    chat.participants = [user, user2]

    session.add(chat)
    await session.commit()
    await session.refresh(chat)

    msg = Message(
        chat_id=chat.id,
        sender_id=user.id,
        text="Unread message",
        is_read=False
    )
    session.add(msg)
    await session.commit()
    await session.refresh(msg)

    return chat
