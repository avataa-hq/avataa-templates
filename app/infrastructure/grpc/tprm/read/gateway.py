import pickle

import grpc

from application.template_parameter.create.exceptions import GrpcInventoryError
from domain.parameter_validation.aggregate import InventoryTprmAggregate
from domain.parameter_validation.query import TPRMReader
from domain.parameter_validation.vo.validation_filter import (
    ParameterValidationFilter,
)
from grpc_clients.inventory.protobuf.mo_info import (
    mo_info_pb2,
    mo_info_pb2_grpc,
)
from infrastructure.grpc.base_grpc_repo import BaseGRPCRepository
from infrastructure.grpc.tprm.read.mappers import grpc_to_domain


class GrpcTPRMReaderRepository(BaseGRPCRepository, TPRMReader):
    def __init__(self):
        super().__init__("inventory")

    async def _get_stub(self) -> mo_info_pb2_grpc.InformerStub:
        channel = await self._get_channel()
        return mo_info_pb2_grpc.InformerStub(channel)

    async def get_all_tprms_by_tmo_id(
        self, grpc_filter: ParameterValidationFilter
    ) -> dict[int, InventoryTprmAggregate]:
        result: dict[int, InventoryTprmAggregate] = {}
        try:
            stub = await self._get_stub()
            msg = mo_info_pb2.RequestGetAllTPRMSByTMOId(
                tmo_id=grpc_filter.tmo_id
            )
            resp = stub.GetAllTPRMSByTMOId(msg)
            async for grpc_chunk in resp:
                data = [
                    pickle.loads(bytes.fromhex(item))
                    for item in grpc_chunk.tprms_data
                ]
                for el in data:
                    aggr = grpc_to_domain(el)
                    result[aggr.id] = aggr
        except grpc.RpcError as ex:
            print(ex)
            raise GrpcInventoryError(status_code=422, detail="Inventory error.")
        return result
