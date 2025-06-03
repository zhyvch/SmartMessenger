import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware

from src.api.exception_handlers import exception_registry

from src.databases import init_mongo
from src.settings.config import settings
from src.api.v1.routers import v1_router, v1_ws_router



logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_mongo()
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

    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie='session',
        max_age=3600,
        same_site='lax',
    )

    app.include_router(v1_router, prefix=settings.API_V1_PREFIX)
    app.include_router(v1_ws_router, prefix=settings.API_V1_PREFIX)
    exception_registry(app)

    return app


if __name__ == '__main__' and not settings.DOCKER_RUN:
    import uvicorn

    uvicorn.run(
        'src.api.main:create_app',
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
