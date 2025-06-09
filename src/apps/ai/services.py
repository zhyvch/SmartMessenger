import logging
from dataclasses import dataclass

from fastapi import HTTPException
from openai import OpenAI

from src.apps.ai.prompts import system_prompt


logger = logging.getLogger(__name__)


@dataclass
class OpenAIService:
    client: OpenAI

    async def ask(self, user_input: str) -> str:
        try:
            response = self.client.chat.completions.create(
                model='gpt-4o-mini',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_input},
                ],
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f'OpenAI API error: {e}')
            raise HTTPException(status_code=500, detail='Internal Server Error')
