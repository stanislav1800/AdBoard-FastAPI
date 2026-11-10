from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from app.core.config import settings
from app.api import router as api_router
from app.ws.router import router as ws_router
from app.core.logging import setup_logging
from app.ws.runtime import start_ws_runtime, stop_ws_runtime

setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = Redis.from_url(settings.redis_url, decode_responses=True)
    app.state.ws = await start_ws_runtime(redis)
    yield
    await stop_ws_runtime(app.state.ws)
    await redis.aclose()

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api")
app.include_router(ws_router, prefix="/ws")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)
