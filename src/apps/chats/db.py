from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from src.apps.chats.models.chats import ChatModel, MessageModel
from src.settings.config import settings


async def init_mongo():
    client = AsyncIOMotorClient(settings.MONGODB_URL)

    await init_beanie(
        database=client[settings.MONGODB_DB],
        document_models=[ChatModel, MessageModel]
    )
