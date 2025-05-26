import logging
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_PATH: Path = Path(__file__).resolve().parent.parent.parent

    DOCKER_RUN: bool = False

    API_HOST: str = '127.0.0.1'
    API_PORT: int = 8000
    API_V1_PREFIX: str = '/api/v1'
    API_DOCS_URL: str = '/api/docs'

    DEBUG: bool = True

    LOG_LEVEL: int = logging.WARNING  # one of logging.getLevelNamesMapping().values()
    LOG_FORMAT: str = '[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)s - %(message)s'

    PG_USER: str
    PG_PASSWORD: str
    PG_HOST: str
    PG_PORT: int
    PG_DATABASE: str

    MONGODB_USER: str
    MONGODB_PASSWORD: str
    MONGODB_HOST: str
    MONGODB_PORT: int
    MONGODB_DB: str

    SECRET_KEY: str


    @property
    def POSTGRES_URL(self):
        return (
            f'postgresql+asyncpg://{self.PG_USER}:'
            f'{self.PG_PASSWORD}@'
            f'{self.PG_HOST}:'
            f'{5432 if self.DOCKER_RUN else self.PG_PORT}/'
            f'{self.PG_DATABASE}'
        )

    @property
    def MONGODB_URL(self) -> str:
        return (
            f'mongodb://'
            f'{self.MONGODB_USER}:'
            f'{self.MONGODB_PASSWORD}@'
            f'{self.MONGODB_HOST}:'
            f'{27017 if self.DOCKER_RUN else self.MONGODB_PORT}/'
            f'{self.MONGODB_DB}'
            f'?authSource=admin'
        )


    model_config = SettingsConfigDict(
        env_file=BASE_PATH / '.env',
    )


settings = Settings()  # type: ignore
