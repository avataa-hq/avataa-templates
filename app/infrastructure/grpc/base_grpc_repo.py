from abc import ABC

import grpc

from infrastructure.grpc.channel_manager import GRPCChannelManager


class BaseGRPCRepository(ABC):
    def __init__(self, service_name: str):
        self._service_name = service_name

    async def _get_channel(self) -> grpc.Channel:
        return await GRPCChannelManager.get_channel(self._service_name)
