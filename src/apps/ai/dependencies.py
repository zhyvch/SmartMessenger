from typing import Annotated

from fastapi import Depends
from openai import OpenAI

from src.apps.ai.services import OpenAIService
from src.settings.config import settings


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_openai_service() -> OpenAIService:
    return OpenAIService(client)


OpenAIServiceDep = Annotated[OpenAIService, Depends(get_openai_service)]
