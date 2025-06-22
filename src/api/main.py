import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.api.exception_handlers import exception_registry
from src.api.v1.routers import v1_router, v1_ws_router
from src.databases import init_mongo
from src.settings.config import settings

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=settings.LOG_FORMAT,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongo_client = AsyncIOMotorClient(settings.MONGODB_URL)
    await init_mongo(mongo_client)

    yield

    mongo_client.close()
    logging.info('MongoDB connection closed')


def create_app():
    app = FastAPI(
        title='SmartMessenger',
        description='Smart messenger API',
        docs_url=settings.API_DOCS_URL,
        debug=settings.DEBUG,
        lifespan=lifespan,
        servers=[{'url': f'http://{settings.API_HOST}:{settings.API_PORT}'}],
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
        allow_headers=['Authorization', 'Content-Type'],
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
