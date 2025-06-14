from fastapi import APIRouter, status, Depends, Query

from src.apps.ai.dependencies import OpenAIServiceDep
from src.apps.ai.schemas import AskResponseSchema, AskSchema
from src.apps.ai.services import UnsplashService
from src.apps.ai.dependencies import get_unsplash_service

ai_router = APIRouter()


@ai_router.post(
    '/ask',
    summary='Ask in AI',
    description='Get an AI response to a user query',
    status_code=status.HTTP_200_OK,
    response_model=AskResponseSchema,
)
async def ask_question(
    schema: AskSchema,
    service: OpenAIServiceDep,
):
    answer = await service.ask(schema.user_input)
    return {'response': answer}

@ai_router.get(
    "/photo",
    summary="Search photo from Unsplash",
    description="Return photo URL by query",
    status_code=status.HTTP_200_OK,
)
async def get_photo(
    query: str = Query(..., min_length=1),
    service: UnsplashService = Depends(get_unsplash_service),
):
    image_url = await service.search_photo(query)
    return {"image_url": image_url}