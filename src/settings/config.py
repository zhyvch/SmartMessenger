import logging
from pathlib import Path
from pydantic import EmailStr
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

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str

    MONGODB_USER: str
    MONGODB_PASSWORD: str
    MONGODB_HOST: str
    MONGODB_PORT: int
    MONGODB_DB: str

    SECRET_KEY: str

    JWT_ALGORITHM: str = 'HS256'
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str

    OPENAI_API_KEY: str
    UNSPLASH_ACCESS_KEY: str

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: EmailStr
    MAIL_PORT: int = 587
    MAIL_SERVER: str
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    MAIL_FROM_NAME: str = "SmartMessenger"

    @property
    def POSTGRES_URL(self) -> str:
        return (
            f'postgresql+asyncpg://'
            f'{self.POSTGRES_USER}:'
            f'{self.POSTGRES_PASSWORD}@'
            f'{self.POSTGRES_HOST}:'
            f'{5432 if self.DOCKER_RUN else self.POSTGRES_PORT}/'
            f'{self.POSTGRES_DB}'
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
