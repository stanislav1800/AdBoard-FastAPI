import asyncio

import pytest

from app.ws.runtime import start_ws_runtime, stop_ws_runtime


class FakeWebSocket:
    def __init__(self, fail: bool = False):
        self.fail = fail
        self.received: list[dict] = []
        self.closed_code: int | None = None

    async def send_json(self, message: dict):
        if self.fail:
            raise RuntimeError("Cannot call send once a close message has been sent")
        self.received.append(message)

    async def close(self, code: int = 1000):
        self.closed_code = code


async def wait_for(condition, timeout: float = 2.0):
    async def _poll():
        while not condition():
            await asyncio.sleep(0.01)
    await asyncio.wait_for(_poll(), timeout)


@pytest.fixture
async def other_worker(redis):
    """Второй воркер с тем же Redis"""
    runtime = await start_ws_runtime(redis)
    yield runtime
    await stop_ws_runtime(runtime)


@pytest.mark.asyncio
async def test_event_delivered_to_other_worker(ws_runtime, other_worker):
    ws = FakeWebSocket()
    await other_worker.manager.subscribe(ws, "chat:1")

    await ws_runtime.events.chat_message(1, {"chat_id": 1, "sender_id": 2, "text": "hi"})

    await wait_for(lambda: ws.received)
    assert ws.received == [{"type": "new_message", "chat_id": 1, "sender_id": 2, "text": "hi"}]

@pytest.mark.asyncio
async def test_unsubscribed_socket_gets_nothing(ws_runtime):
    ws, other = FakeWebSocket(), FakeWebSocket()
    await ws_runtime.manager.subscribe(ws, "chat:1")
    await ws_runtime.manager.subscribe(other, "chat:1")
    await ws_runtime.manager.unsubscribe(ws, "chat:1")

    await ws_runtime.events.chat_message(1, {"text": "hi"})

    await wait_for(lambda: other.received)
    assert ws.received == []

@pytest.mark.asyncio
async def test_dead_socket_dropped_others_still_receive(ws_runtime):
    dead, alive = FakeWebSocket(fail=True), FakeWebSocket()
    manager = ws_runtime.manager
    await manager.subscribe(dead, "chat:1")
    await manager.subscribe(dead, "user:1")
    await manager.subscribe(alive, "chat:1")

    await ws_runtime.events.chat_message(1, {"text": "hi"})

    await wait_for(lambda: alive.received)
    await wait_for(lambda: dead.closed_code is not None)
    assert dead.closed_code == 1011
    
    assert not manager.is_topic_active("user:1")
    assert manager.is_topic_active("chat:1")

@pytest.mark.asyncio
async def test_broker_unsubscribed_when_last_socket_leaves(ws_runtime, redis):
    ws = FakeWebSocket()
    await ws_runtime.manager.subscribe(ws, "chat:7")
    assert dict(await redis.pubsub_numsub("ws:chat:7"))["ws:chat:7"] == 1

    await ws_runtime.manager.unsubscribe_all(ws)
    assert dict(await redis.pubsub_numsub("ws:chat:7"))["ws:chat:7"] == 0

@pytest.mark.asyncio
async def test_publish_failure_does_not_raise(ws_runtime, monkeypatch):
    async def broken_publish(*args, **kwargs):
        raise ConnectionError("redis down")
    monkeypatch.setattr(ws_runtime.manager._broker, "publish", broken_publish)

    await ws_runtime.events.chat_message(1, {"text": "hi"})

@pytest.mark.asyncio
async def test_presence_expires_without_heartbeat(ws_runtime, monkeypatch):
    presence = ws_runtime.presence
    await presence.touch(1, "conn-a")
    assert await presence.is_online(1)

    import app.ws.presence as presence_module
    real_time = presence_module.time.time
    monkeypatch.setattr(presence_module.time, "time", lambda: real_time() + presence.ttl + 1)
    assert not await presence.is_online(1)
