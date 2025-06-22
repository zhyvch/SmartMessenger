from typing import Annotated

from fastapi import Depends
from openai import OpenAI

from src.apps.ai.services import OpenAIService, UnsplashService
from src.apps.users.models import User
from src.apps.users.routers.auth import get_current_user
from src.settings.config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_openai_service() -> OpenAIService:
    return OpenAIService(client)


def get_unsplash_service() -> UnsplashService:
    return UnsplashService(access_key=settings.UNSPLASH_ACCESS_KEY)


CurrentUserDep = Annotated[User, Depends(get_current_user)]

OpenAIServiceDep = Annotated[OpenAIService, Depends(get_openai_service)]
UnsplashServiceDep = Annotated[UnsplashService, Depends(get_unsplash_service)]
