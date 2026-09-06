from typing import AsyncGenerator
from redis.asyncio import Redis, ConnectionPool

from reachout.src.core.config import settings


pool = ConnectionPool.from_url(
    url=f"{settings.REDIS_URL}/0",
    max_connections=10,
    decode_responses=True
)

async def get_redis() -> AsyncGenerator[Redis, None]:
    async with Redis(connection_pool=pool) as client:
        yield client