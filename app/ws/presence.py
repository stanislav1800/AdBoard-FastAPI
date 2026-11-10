import time

from redis.asyncio import Redis


class PresenceService:
    """
    Онлайн-статус пользователей в Redis, общий для всех воркеров.

    presence:{user_id} — ZSET: id соединения -> момент истечения.
    Живое соединение продлевает себя heartbeat'ом. Если воркер упал,
    его соединения просто истекают по TTL, без ручной чистки.
    """

    def __init__(self, redis: Redis, ttl: int = 60):
        self._redis = redis
        self.ttl = ttl

    @staticmethod
    def _key(user_id: int) -> str:
        return f"presence:{user_id}"

    async def touch(self, user_id: int, connection_id: str):
        """Отметить соединение живым (подключение и heartbeat)"""
        now = time.time()
        key = self._key(user_id)
        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(key, "-inf", now)
            pipe.zadd(key, {connection_id: now + self.ttl})
            pipe.expire(key, self.ttl)
            await pipe.execute()

    async def disconnect(self, user_id: int, connection_id: str):
        await self._redis.zrem(self._key(user_id), connection_id)

    async def is_online(self, user_id: int) -> bool:
        return await self._redis.zcount(self._key(user_id), time.time(), "+inf") > 0
