from contextlib import AbstractAsyncContextManager
from typing import Any, Annotated, Callable
from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from app.core.config import settings
from app.models.base import Base

async_engine = create_async_engine(settings.get_db_url(), echo=True)
async_session = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

async def init_db() -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, Any]:
    async with async_session() as session:
        yield session

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]

SessionFactory = Callable[[], AbstractAsyncContextManager[AsyncSession]]

def get_session_factory() -> SessionFactory:
    """
    Для долгоживущих соединений (WebSocket): сессия открывается
    на время одной операции, а не на всё время соединения.
    """
    return async_session

SessionFactoryDep = Annotated[SessionFactory, Depends(get_session_factory)]
