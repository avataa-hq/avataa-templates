from functools import partial
import time
from typing import Any, Callable, Literal, Self
from urllib.parse import urlunparse

from keycloak import KeycloakOpenID
from pydantic import Field, computed_field, field_validator
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class KeycloakConfig(BaseSettings):
    realm: str = Field(
        default="example",
        min_length=1,
        serialization_alias="realm_name",
    )
    client_id: str = Field(default="kafka", min_length=1)
    client_secret: str = Field(
        default="secret",
        serialization_alias="client_secret_key",
    )
    protocol: Literal["http", "https"] = Field(default="https")
    host: str = Field(default="localhost", min_length=1)
    port: int = Field(default=443, gt=0, lt=65536)

    @computed_field  # type: ignore
    @property
    def url(self) -> str:
        url = urlunparse(
            (str(self.protocol), f"{self.host}:{self.port}", "auth", "", "", "")
        )
        return str(url)

    model_config = SettingsConfigDict(env_prefix="keycloak_")


class KafkaConfig(BaseSettings):
    # Config example for correct work Kafka client
    # https://github.com/confluentinc/librdkafka/blob/master/CONFIGURATION.md
    turn_on: bool = Field(default=False)
    secured: bool = Field(default=False)
    inventory_changes_topic: str = Field("inventory.changes")
    bootstrap_servers: str = Field(
        "kafka",
        serialization_alias="bootstrap.servers",
        validation_alias="kafka_url",
        min_length=1,
    )
    group_id: str = Field(
        "object-templates",
        serialization_alias="group.id",
        min_length=1,
    )
    auto_offset_reset: Literal["earliest", "latest", "none"] = Field(
        "earliest",
        serialization_alias="auto.offset.reset",
        validation_alias="kafka_consumer_offset",
    )
    enable_auto_commit: bool = Field(
        False,
        serialization_alias="enable.auto.commit",
    )
    sasl_mechanism: Literal["OAUTHBEARER", None] = Field(
        None,
        serialization_alias="sasl.mechanisms",
    )
    security_protocol_raw: Literal[
        "plaintext", "sasl_plaintext", "sasl_ssl", "ssl", None
    ] = Field(None, validation_alias="kafka_security_protocol")

    @field_validator("security_protocol_raw", mode="before")
    @classmethod
    def normalize_security_protocol(cls, value: Any) -> Any:
        if isinstance(value, str):
            return value.lower()
        else:
            return value

    @computed_field  # type: ignore
    @property
    def oauth_cb(
        self,
    ) -> None | Callable[[None, KeycloakConfig], tuple[str, float]]:
        if not self.sasl_mechanism:
            return None
        keycloak_config = KeycloakConfig()
        return partial(
            self._get_token_for_kafka_producer,
            keycloak_config=keycloak_config,
        )

    @computed_field  # type: ignore
    @property
    def security_protocol(self) -> str:
        if self.secured:
            return str(self.security_protocol_raw) or "sasl_plaintext"
        return "plaintext"

    @staticmethod
    def _get_token_for_kafka_producer(
        conf: Any,
        keycloak_config: KeycloakConfig,
    ) -> tuple[str, float]:
        keycloak_openid = KeycloakOpenID(
            server_url=keycloak_config.url,
            client_id=keycloak_config.client_id,
            realm_name=keycloak_config.realm,
            client_secret_key=keycloak_config.client_secret,
        )
        attempt = 5
        token = ""
        expires_in = 1.0
        while attempt > 0:
            try:
                tkn = keycloak_openid.token(grant_type="client_credentials")
                token = tkn["access_token"]
                expires_in = float(tkn["expires_in"]) * 0.95
            except Exception as ex:
                print(ex)
                time.sleep(1)
                attempt -= 1
            else:
                if tkn:
                    break
                else:
                    time.sleep(1)
                    attempt -= 1
                    continue
        # print(f"KEYCLOAK TOKEN FOR KAFKA: ...{tkn['access_token'][-3:]} EXPIRED_TIME:{expires_in}.")
        return token, time.time() + expires_in

    def get_config(self: Self, **kwargs: Any) -> dict[str, Any]:
        data = self.model_dump(**kwargs)
        data["security.protocol"] = self.security_protocol
        return data

    model_config = SettingsConfigDict(env_prefix="kafka_")
