from typing import Annotated

from fastapi import Depends
from openai import OpenAI

from src.apps.ai.services import OpenAIService
from src.apps.ai.services import UnsplashService
from src.settings.config import settings


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_openai_service() -> OpenAIService:
    return OpenAIService(client)

def get_unsplash_service() -> UnsplashService:
    return UnsplashService(access_key=settings.UNSPLASH_ACCESS_KEY)

OpenAIServiceDep = Annotated[OpenAIService, Depends(get_openai_service)]
UnsplashServiceDep = Annotated[UnsplashService, Depends(get_unsplash_service)]
