from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends
from starlette.requests import HTTPConnection
from redis.asyncio import Redis

from app.ws.broker import RedisPubSubBroker
from app.ws.chat import WSEventService
from app.ws.manager import ConnectionManager
from app.ws.presence import PresenceService


@dataclass
class WSRuntime:
    manager: ConnectionManager
    presence: PresenceService
    events: WSEventService


async def start_ws_runtime(redis: Redis) -> WSRuntime:
    manager = ConnectionManager(RedisPubSubBroker(redis))
    presence = PresenceService(redis)
    await manager.start()
    return WSRuntime(
        manager=manager,
        presence=presence,
        events=WSEventService(manager, presence),
    )


async def stop_ws_runtime(runtime: WSRuntime):
    await runtime.manager.stop()


def get_ws_runtime(conn: HTTPConnection) -> WSRuntime:
    return conn.app.state.ws

def get_ws_service(conn: HTTPConnection) -> WSEventService:
    return conn.app.state.ws.events

WSRuntimeDep = Annotated[WSRuntime, Depends(get_ws_runtime)]
WSEventServiceDep = Annotated[WSEventService, Depends(get_ws_service)]
