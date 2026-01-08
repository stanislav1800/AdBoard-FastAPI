
from fastapi import FastAPI

from app.core.config import settings
from app.api import router as api_router
from app.ws.router import router as ws_router
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
)

app.include_router(api_router, prefix="/api")
app.include_router(ws_router, prefix="/ws")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port)
