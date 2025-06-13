from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase


from src.settings.config import settings


async def init_mongo():
    from src.apps.chats.models import ChatModel, MessageModel, ChatPermissionsModel
    client = AsyncIOMotorClient(settings.MONGODB_URL)

    await init_beanie(
        database=client[settings.MONGODB_DB],
        document_models=[ChatModel, MessageModel, ChatPermissionsModel]
    )

engine = create_async_engine(
    url=settings.POSTGRES_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)


session_factory = async_sessionmaker(autoflush=False, bind=engine)


class Base(DeclarativeBase):
    def __repr__(self):
        return f'<{self.__class__.__name__} {self.__dict__}>'

async def init_postgres():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_db() -> AsyncSession:
    async with session_factory() as session:
        yield session
