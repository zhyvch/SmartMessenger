import logging
from dataclasses import dataclass

import httpx
from openai import APIError, AuthenticationError, OpenAI, OpenAIError, RateLimitError

from src.apps.ai.exceptions import OpenAIServiceException, UnsplashServiceException
from src.apps.ai.prompts import system_prompt

logger = logging.getLogger(__name__)


@dataclass
class OpenAIService:
    client: OpenAI

    async def ask(self, user_input: str) -> str:
        try:
            response = await self.client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[
                    {'role': 'system', 'content': system_prompt},
                    {'role': 'user', 'content': user_input},
                ],
                max_tokens=150,
            )
            return response.choices[0].message.content
        except RateLimitError as e:
            logger.error(f'OpenAI rate limit exceeded: {str(e)}')
            raise OpenAIServiceException(
                'OpenAI rate limit exceeded. Please try again later.'
            )
        except AuthenticationError as e:
            logger.error(f'OpenAI authentication error: {str(e)}')
            raise OpenAIServiceException('Authentication error with OpenAI service.')
        except APIError as e:
            logger.error(f'OpenAI API error: {str(e)}')
            raise OpenAIServiceException('OpenAI API error. Please try again later.')
        except OpenAIError as e:
            logger.error(f'OpenAI error: {str(e)}')
            raise OpenAIServiceException(f'Error communicating with OpenAI: {str(e)}')
        except Exception as e:
            logger.error(f'Unexpected error in OpenAI service: {str(e)}')
            raise OpenAIServiceException(
                'Unexpected error occurred while processing your request.'
            )


@dataclass
class UnsplashService:
    access_key: str
    base_url: str = 'https://api.unsplash.com'

    async def search_photo(self, query: str) -> str:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f'{self.base_url}/search/photos',
                    params={'query': query, 'per_page': 1},
                    headers={'Authorization': f'Client-ID {self.access_key}'},
                    timeout=10.0,
                )

                response.raise_for_status()

                data = response.json()
                if not data.get('results') or len(data['results']) == 0:
                    return f'No photos found for query: {query}'

                return data['results'][0]['urls']['regular']

        except httpx.TimeoutException:
            logger.error(f'Timeout while searching Unsplash for: {query}')
            raise UnsplashServiceException(
                'Unsplash service timed out. Please try again later.'
            )
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            logger.error(f'HTTP error {status_code} from Unsplash: {str(e)}')

            if status_code == 401:
                raise UnsplashServiceException(
                    'Authentication error with Unsplash service.'
                )
            elif status_code == 403:
                raise UnsplashServiceException('Access forbidden to Unsplash service.')
            elif status_code == 429:
                raise UnsplashServiceException(
                    'Unsplash rate limit exceeded. Please try again later.'
                )
            else:
                raise UnsplashServiceException(
                    f'Unsplash service error (HTTP {status_code}).'
                )
        except Exception as e:
            logger.error(f'Unexpected error in Unsplash service: {str(e)}')
            raise UnsplashServiceException(
                'Unexpected error occurred while processing your request.'
            )
