from functools import lru_cache

from pydantic import (
    Field,
    PostgresDsn,
    computed_field,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class ApplicationSettings(BaseSettings):
    docs_enabled: bool = Field(
        default=True, alias="docs_enabled"
    )
    custom_enabled: bool = Field(default=False)
    redoc_js_url: str = Field(default="")
    swagger_js_url: str = Field(default="")
    swagger_css_url: str = Field(default="")

    model_config = SettingsConfigDict(
        env_prefix="docs_"
    )


class DatabaseSettings(BaseSettings):
    schema_name: str = Field(default="public")
    db_type: str = Field(
        default="postgresql", alias="db_type"
    )
    user: str = Field(default="templates_admin")
    db_pass: str = Field(
        default="password", alias="db_pass"
    )
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    name: str = Field(default="templates")

    model_config = SettingsConfigDict(
        env_prefix="db_"
    )


class InventorySettings(BaseSettings):
    host: str = Field(
        default="localhost", min_length=1
    )
    grpc_port: int = Field(default=50051, ge=0)

    @computed_field
    @property
    def grpc_url(self) -> str:
        _url = f"{self.host}:{self.port}"
        return _url

    model_config = SettingsConfigDict(
        env_prefix="inventory_"
    )


class Config(object):
    app: ApplicationSettings = (
        ApplicationSettings()
    )
    db: DatabaseSettings = DatabaseSettings()
    inventory: InventorySettings = (
        InventorySettings()
    )
    DATABASE_URL: PostgresDsn = PostgresDsn(
        f"{db.db_type}://{db.user}:{db.db_pass}@{db.host}:{db.port}/{db.name}",
    )


@lru_cache
def setup_config() -> Config:
    settings = Config()
    return settings
