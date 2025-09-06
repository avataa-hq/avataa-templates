from logging import getLogger
import pickle

import grpc

from application.template_parameter.create.exceptions import GrpcInventoryError
from domain.tmo_validation.aggregate import InventoryTMOAggregate
from domain.tmo_validation.query import TMOReader
from grpc_clients.inventory.protobuf.mo_info import (
    mo_info_pb2,
    mo_info_pb2_grpc,
)
from infrastructure.grpc.base_grpc_repo import BaseGRPCRepository
from infrastructure.grpc.tmo.read.mappers import grpc_to_domain


class GrpcTMOReaderRepository(BaseGRPCRepository, TMOReader):
    def __init__(self):
        super().__init__("inventory")
        self.logger = getLogger(self.__class__.__name__)

    async def _get_stub(self) -> mo_info_pb2_grpc.InformerStub:
        channel = await self._get_channel()
        return mo_info_pb2_grpc.InformerStub(channel)

    async def get_all_tmo_data(self) -> list[InventoryTMOAggregate]:
        try:
            stub = await self._get_stub()
            msg = mo_info_pb2.GetAllTMORequest()
            resp = await stub.GetAllTMO(msg)
            data = [pickle.loads(bytes.fromhex(item)) for item in resp.tmo_info]
            return [grpc_to_domain(el) for el in data]
        except grpc.RpcError as ex:
            self.logger.exception(ex)
            raise GrpcInventoryError(status_code=422, detail="Inventory error.")
