from fastapi import APIRouter, Depends, Query, status

from src.apps.ai.dependencies import (
    CurrentUserDep,
    OpenAIServiceDep,
    get_unsplash_service,
)
from src.apps.ai.schemas import AskResponseSchema, AskSchema
from src.apps.ai.services import UnsplashService

ai_router = APIRouter()


@ai_router.post(
    "/ask",
    summary="Ask in AI",
    description="Get an AI response to a user query",
    status_code=status.HTTP_200_OK,
    response_model=AskResponseSchema,
)
async def ask_question(
    schema: AskSchema,
    user: CurrentUserDep,
    service: OpenAIServiceDep,
):
    answer = await service.ask(schema.user_input)
    return {"response": answer}


@ai_router.get(
    "/photo",
    summary="Search photo from Unsplash",
    description="Return photo URL by query",
    status_code=status.HTTP_200_OK,
)
async def get_photo(
    user: CurrentUserDep,
    query: str = Query(..., min_length=1),
    service: UnsplashService = Depends(get_unsplash_service),
):
    image_url = await service.search_photo(query)
    return {"image_url": image_url}
