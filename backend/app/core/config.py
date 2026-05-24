from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'FactoryBridge API'
    app_version: str = '0.19.3-retest-hardening'
    api_prefix: str = '/api/v1'
    environment: str = Field(default='development', alias='APP_ENV')
    cors_origins_raw: str = Field(default='http://localhost:3000', alias='BACKEND_CORS_ORIGINS')

    database_url: str = Field(default='sqlite+pysqlite:///./factorybridge_dev.db', alias='DATABASE_URL')
    redis_url: str = Field(default='redis://redis:6379/0', alias='REDIS_URL')
    secret_key: str = Field(default='dev-only-change-me', alias='SECRET_KEY')

    @property
    def cors_origins(self) -> list[str]:
        return [item.strip() for item in self.cors_origins_raw.split(',') if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
