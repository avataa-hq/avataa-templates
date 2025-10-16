from functools import lru_cache
from typing import Any, Literal, Self
from urllib.parse import urlunparse

from pydantic import Field, computed_field, field_validator
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class KafkaConfig(BaseSettings):
    # Config example for correct work Kafka client
    # https://github.com/confluentinc/librdkafka/blob/master/CONFIGURATION.md
    turn_on: bool = Field(default=True)
    secured: bool = Field(default=False, validation_alias="kafka_with_keycloak")
    inventory_changes_topic: str = Field(default="inventory.changes")
    bootstrap_servers: str = Field(
        default="kafka:9092",
        min_length=1,
        serialization_alias="bootstrap.servers",
        validation_alias="kafka_url",
    )
    group_id: str = Field(
        default="Object_Templates",
        min_length=1,
        serialization_alias="group.id",
    )
    auto_offset_reset: Literal["earliest", "latest", "none"] = Field(
        default="earliest",
        serialization_alias="auto.offset.reset",
        validation_alias="kafka_consumer_offset",
    )
    enable_auto_commit: bool = Field(
        default=False,
        serialization_alias="enable.auto.commit",
    )
    sasl_mechanism: Literal["OAUTHBEARER", None] = Field(
        default=None,
        serialization_alias="sasl.mechanisms",
    )
    security_protocol_raw: Literal[
        "plaintext", "sasl_plaintext", "sasl_ssl", "ssl", None
    ] = Field(default=None, validation_alias="kafka_security_protocol")

    # Token config
    # KIP-1139 available in librdkafka 2.11.0 and above
    method: str = Field(
        default="oidc", serialization_alias="sasl.oauthbearer.method"
    )
    # example: "profile openid"
    scope: str = Field(
        default="profile", serialization_alias="sasl.oauthbearer.scope"
    )

    keycloak_client_id: str = Field(
        default="kafka",
        min_length=1,
        serialization_alias="sasl.oauthbearer.client.id",
        validation_alias="keycloak_client_id",
    )
    keycloak_client_secret: str = Field(
        ...,
        min_length=1,
        serialization_alias="sasl.oauthbearer.client.secret",
        validation_alias="keycloak_client_secret",
    )
    keycloak_protocol: Literal["http", "https"] = Field(
        default="http", validation_alias="keycloak_protocol"
    )
    keycloak_host: str = Field(
        default="keycloak", min_length=1, validation_alias="keycloak_host"
    )
    keycloak_port: int = Field(
        default=8080, ge=1, le=65_535, validation_alias="keycloak_port"
    )
    realm: str = Field(
        default="avataa", min_length=1, validation_alias="keycloak_realm"
    )

    @computed_field(alias="sasl.oauthbearer.token.endpoint.url")  # type: ignore
    @property
    def keycloak_token_url(self) -> str:
        url = urlunparse(
            (
                str(self.keycloak_protocol),
                f"{self.keycloak_host}:{self.keycloak_port}",
                f"realms/{self.realm}/protocol/openid-connect/token",
                "",
                "",
                "",
            )
        )
        return str(url)

    @field_validator("security_protocol_raw", mode="before")
    @classmethod
    def normalize_security_protocol(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.lower()
        else:
            return value

    @computed_field  # type: ignore
    @property
    def security_protocol(self) -> str:
        if self.secured:
            return str(self.security_protocol_raw) or "sasl_plaintext"
        return "plaintext"

    def get_config(self: Self, **kwargs: Any) -> dict[str, Any]:
        data = self.model_dump(**kwargs)
        data["security.protocol"] = self.security_protocol
        return data

    model_config = SettingsConfigDict(env_prefix="kafka_")


@lru_cache
def get_config() -> KafkaConfig:
    return KafkaConfig()
