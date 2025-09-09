from functools import lru_cache
from typing import Literal

from pydantic import (
    Field,
    PostgresDsn,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class ApplicationSettings(BaseSettings):
    docs_enabled: bool = Field(default=True, alias="docs_enabled")
    custom_enabled: bool = Field(default=False)
    redoc_js_url: str = Field(default="")
    swagger_js_url: str = Field(default="")
    swagger_css_url: str = Field(default="")
    app_title: str = "Object Templates"
    prefix: str = f"/api/{app_title.replace(' ', '_').lower()}"
    app_version: str = "1"
    logging: int = Field(default=20, ge=0, le=50, alias="logging")
    log_with_time: bool = Field(default=False, alias="log_with_time")

    model_config = SettingsConfigDict(env_prefix="docs_")


class DatabaseSettings(BaseSettings):
    schema_name: str = Field(default="public")
    db_type: str = Field(
        default="postgresql+asyncpg",
        alias="db_type",
    )
    user: str = Field(default="templates_admin")
    db_pass: str = Field(default="password", alias="db_pass")
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    name: str = Field(default="templates")

    model_config = SettingsConfigDict(env_prefix="db_")


class InventorySettings(BaseSettings):
    host: str = Field(default="localhost", min_length=1)
    grpc_port: int = Field(default=50051, ge=0)

    @computed_field  # type: ignore[misc]
    @property
    def grpc_url(self) -> str:
        _url = f"{self.host}:{self.grpc_port}"
        return _url

    model_config = SettingsConfigDict(env_prefix="inventory_")


class TestsConfig(BaseSettings):
    run_container_postgres_local: bool = Field(
        default=True,
        alias="tests_run_container_postgres_local",
    )
    db_type: str = Field(
        default="postgresql+asyncpg",
        alias="tests_db_type",
    )
    user: str = Field(default="test_user")
    db_pass: str = Field(default="password", alias="tests_db_pass")
    host: str = Field(default="localhost")
    port: int = Field(default=5432)
    name: str = Field(default="templates")
    docker_db_host: str = Field(
        default="localhost",
        alias="test_docker_db_host",
    )

    model_config = SettingsConfigDict(env_prefix="tests_db_")


class SecurityConfig(BaseSettings):
    admin_role: str = Field(default="__admin")
    security_type: str = Field(default="DISABLE")

    @field_validator("security_type", mode="before")
    @classmethod
    def normalize_security_type(cls, value: str) -> str:
        if isinstance(value, str):
            return value.upper()
        else:
            return value

    keycloak_protocol: Literal["http", "https"] = Field(default="http")
    keycloak_host: str = Field(
        default="localhost", min_length=1, validation_alias="keycloak_host"
    )
    keycloak_port: int | None = Field(
        default=None, gt=0, validation_alias="keycloak_port"
    )
    keycloak_redirect_protocol_raw: Literal["http", "https", None] = Field(
        default=None, validation_alias="keycloak_redirect_protocol"
    )
    keycloak_redirect_host_raw: str | None = Field(
        default=None, min_length=1, validation_alias="keycloak_redirect_host"
    )
    keycloak_redirect_port_raw: int | None = Field(
        default=None, gt=0, validation_alias="keycloak_redirect_port"
    )
    realm: str = Field(
        default="master", min_length=1, validation_alias="keycloak_realm"
    )

    @computed_field  # type: ignore
    @property
    def keycloak_redirect_protocol(self) -> str:
        if self.keycloak_redirect_protocol_raw is None:
            if self.keycloak_protocol is None:
                raise ValueError("keycloak_protocol is None")
            return self.keycloak_protocol
        return self.keycloak_redirect_protocol_raw

    @computed_field  # type: ignore
    @property
    def keycloak_redirect_host(self) -> str:
        if self.keycloak_redirect_host_raw is None:
            return self.keycloak_host
        return self.keycloak_redirect_host_raw

    @computed_field  # type: ignore
    @property
    def keycloak_redirect_port(self) -> int:
        if self.keycloak_redirect_port_raw is None:
            if self.keycloak_port is None:
                raise ValueError("keycloak_port is None")
            return self.keycloak_port
        return self.keycloak_redirect_port_raw

    @computed_field  # type: ignore
    @property
    def keycloak_url(self) -> str:
        url = f"{self.keycloak_protocol}://{self.keycloak_host}"
        if self.keycloak_port:
            url = f"{url}:{self.keycloak_port}"
        return url

    @computed_field  # type: ignore
    @property
    def keycloak_public_key_url(self) -> str:
        return f"{self.keycloak_url}/realms/{self.realm}"

    @computed_field  # type: ignore
    @property
    def keycloak_redirect_url(self) -> str:
        url = (
            f"{self.keycloak_redirect_protocol}://{self.keycloak_redirect_host}"
        )
        if self.keycloak_redirect_port:
            url = f"{url}:{self.keycloak_redirect_port}"
        return url

    @computed_field  # type: ignore
    @property
    def keycloak_token_url(self) -> str:
        return f"{self.keycloak_redirect_url}/realms/{self.realm}/protocol/openid-connect/token"

    @computed_field  # type: ignore
    @property
    def keycloak_authorization_url(self) -> str:
        return f"{self.keycloak_redirect_url}/realms/{self.realm}/protocol/openid-connect/auth"

    opa_protocol: Literal["http", "https"] = Field(default="http")
    opa_host: str = Field(default="opa", min_length=1)
    opa_port: int = Field(default=8181, gt=0)
    opa_policy: str = Field(default="main")

    @computed_field  # type: ignore
    @property
    def opa_url(self) -> str:
        return f"{self.opa_protocol}://{self.opa_host}:{self.opa_port}"

    @computed_field  # type: ignore
    @property
    def opa_policy_path(self) -> str:
        return f"/v1/data/{self.opa_policy}"

    security_middleware_protocol: Literal["http", "https"] | None = Field(
        default=None, validation_alias="security_middleware_protocol"
    )
    security_middleware_host: str | None = Field(default=None, min_length=1)
    security_middleware_port: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def set_defaults(self) -> "SecurityConfig":
        if self.security_middleware_protocol is None:
            self.security_middleware_protocol = self.keycloak_protocol
        if self.security_middleware_host is None:
            self.security_middleware_host = self.keycloak_host
        if self.security_middleware_port is None:
            self.security_middleware_port = self.keycloak_port
        return self

    @computed_field  # type: ignore
    @property
    def security_postfix(self) -> str:
        if (
            self.security_middleware_host == self.keycloak_host
            and self.security_middleware_port == self.keycloak_port
        ):
            url = f"/realms/{self.realm}/protocol/openid-connect/userinfo"
        else:
            url = f"/api/security_middleware/v1/cached/realms/{self.realm}/protocol/openid-connect/userinfo"
        return url

    @computed_field  # type: ignore
    @property
    def security_middleware_url(self) -> str:
        return (
            f"{self.security_middleware_protocol}://{self.security_middleware_host}:{self.security_middleware_port}"
            f"{self.security_postfix}"
        )


class Config(object):
    app: ApplicationSettings = ApplicationSettings()
    db: DatabaseSettings = DatabaseSettings()
    inventory: InventorySettings = InventorySettings()
    tests: TestsConfig = TestsConfig()
    DATABASE_URL: PostgresDsn = PostgresDsn(
        f"{db.db_type}://{db.user}:{db.db_pass}@{db.host}:{db.port}/{db.name}",
    )
    test_database_url: PostgresDsn = PostgresDsn(
        f"{tests.db_type}://{tests.user}:{tests.db_pass}@{tests.host}:{tests.port}/{tests.name}",
    )
    security_config: SecurityConfig = SecurityConfig()


@lru_cache
def setup_config() -> Config:
    settings = Config()
    return settings
