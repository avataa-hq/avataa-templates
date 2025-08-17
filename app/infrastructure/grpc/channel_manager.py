from dataclasses import dataclass

import grpc


@dataclass
class GRPCServiceConfig:
    url: str
    service_name: str
    options: list | None = None


class GRPCChannelManager:
    _channels: dict[str, grpc.Channel] = {}
    _services: dict[str, GRPCServiceConfig] = {}

    @classmethod
    def register_service(cls, service_name: str, config: GRPCServiceConfig):
        cls._services[service_name] = config

    @classmethod
    async def get_channel(cls, service_name: str) -> grpc.Channel:
        if service_name not in cls._services:
            raise ValueError(f"Service {service_name} not registered")

        config = cls._services[service_name]

        if config.url not in cls._channels:
            try:
                if config.options:
                    cls._channels[config.url] = grpc.aio.insecure_channel(
                        config.url, options=config.options
                    )
                else:
                    cls._channels[config.url] = grpc.aio.insecure_channel(
                        config.url
                    )
            except RuntimeError as ex:
                print(ex)
                print("Incorrect loop for grpc")
                raise

        return cls._channels[config.url]

    @classmethod
    async def close_all_channels(cls):
        for channel in cls._channels.values():
            await channel.close()
        cls._channels.clear()
