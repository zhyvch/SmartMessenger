import os
import logging
from fastapi import APIRouter, status, Depends, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from src.api.schemas import ErrorSchema


logger = logging.getLogger(__name__)
router = APIRouter()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

system_prompt = """
You are a text-based AI assistant for a messenger app.

Our messenger is called Smart Messenger.

Users of our app will write to you, and you must help them.

You can perform the following actions:
- Send messages

The functionality of our project:
- Everything that exists in Telegram also exists here.

Respond politely, briefly, and when appropriate — suggest relevant actions.
"""

class AskSchema(BaseModel):
    user_input: str

class AskResponseSchema(BaseModel):
    response: str

class OpenAIService:
    def __init__(self, client: OpenAI):
        self.client = client

    async def ask(self, user_input: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise HTTPException(status_code=500, detail="Internal Server Error")

def get_openai_service() -> OpenAIService:
    return OpenAIService(client)

@router.post(
    "/ask",
    summary="Ask in AI",
    description="Get an AI response to a user query",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": ErrorSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorSchema},
    },
    response_model=AskResponseSchema,
)
async def ask_question(
    schema: AskSchema,
    service: OpenAIService = Depends(get_openai_service),
):
    answer = await service.ask(schema.user_input)
    return {"response": answer}
