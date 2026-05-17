from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://history:history@localhost:5432/history"
    redis_url: str = "redis://localhost:6379"
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_password: SecretStr = SecretStr("history")
    api_env: str = "development"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
