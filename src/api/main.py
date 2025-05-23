import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.settings.config import settings
from src.api.v1.handlers import router as v1_router
from src.api.v1.websocket.handlers import router as v1_ws_router


logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    ...
    yield
    ...


def create_app():
    app = FastAPI(
        title='SmartMessenger',
        description='Smart messenger API',
        docs_url=settings.API_DOCS_URL,
        debug=settings.DEBUG,
        lifespan=lifespan,
    )
    app.include_router(v1_router, prefix=settings.API_V1_PREFIX)
    app.include_router(v1_ws_router, prefix=settings.API_V1_PREFIX)

    return app


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        'src.api.main:create_app',
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
