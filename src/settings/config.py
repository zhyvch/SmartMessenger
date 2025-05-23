import logging
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BASE_PATH: Path = Path(__file__).resolve().parent.parent.parent

    DOCKER_RUN: bool = False

    API_HOST: str = '127.0.0.1'
    API_PORT: int = 8000
    API_V1_PREFIX: str = '/api/v1'
    API_DOCS_URL: str = '/api/docs'
    pg_user: str
    pg_password: str
    pg_database: str

    DEBUG: bool = True

    LOG_LEVEL: int = logging.WARNING  # one of logging.getLevelNamesMapping().values()
    LOG_FORMAT: str = '[%(asctime)s.%(msecs)03d] %(module)10s:%(lineno)-3d %(levelname)s - %(message)s'


    model_config = SettingsConfigDict(
        env_file=BASE_PATH / '.env',
        env_prefix="PG_",
        extra="ignore",
    )


settings = Settings()  # type: ignore
