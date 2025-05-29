from fastapi import APIRouter, status

from src.apps.ai.dependencies import OpenAIServiceDep
from src.apps.ai.schemas import AskResponseSchema, AskSchema


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
