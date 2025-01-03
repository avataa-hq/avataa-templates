import os
from dotenv import load_dotenv
from functools import lru_cache

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class ApplicationSettings(BaseSettings):
    DOCS_ENABLED: bool = Field(default=True)
    DOCS_CUSTOM_ENABLED: bool = Field(default=False)
    REDOC_JS_URL: str = Field(default="")
    SWAGGER_JS_URL: str = Field(default="")
    SWAGGER_CSS_URL: str = Field(default="")


class DatabaseSettings(BaseSettings):
    DB_SCHEMA: str = Field(default="public")
    DATABASE_URL: PostgresDsn = Field(alias="SQLALCHEMY_DATABASE_URL")


class Config(object):
    app: ApplicationSettings = ApplicationSettings()
    db: DatabaseSettings = DatabaseSettings()


load_dotenv()

# SERVICES
INVENTORY_HOST = os.getenv('INVENTORY_HOST', 'localhost')
INVENTORY_GRPC_PORT = os.getenv('INVENTORY_GRPC_PORT', '50051')


@lru_cache
def setup_config() -> Config:
    settings = Config()
    return settings
