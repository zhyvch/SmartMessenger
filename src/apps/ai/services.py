import logging
from dataclasses import dataclass

from fastapi import HTTPException
from openai import OpenAI
import httpx

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

@dataclass
class UnsplashService:
    access_key: str

    async def search_photo(self, query: str) -> str:
        url = "https://api.unsplash.com/search/photos"
        params = {
            "query": query,
            "per_page": 1,
            "client_id": self.access_key,
        }

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)

        data = response.json()
        if not data.get("results"):
            raise HTTPException(status_code=404, detail=f"No results found for '{query}'")

        return data["results"][0]["urls"]["regular"]