import grpc
import pickle
from grpc_clients.inventory.protobuf.mo_info import mo_info_pb2, mo_info_pb2_grpc
from config import INVENTORY_HOST, INVENTORY_GRPC_PORT


async def get_all_tmo_data_from_inventory_channel_in():
    """getter for GetTPRMData"""
    async with grpc.aio.insecure_channel(f'{INVENTORY_HOST}:{INVENTORY_GRPC_PORT}') as async_channel:
        stub = mo_info_pb2_grpc.InformerStub(async_channel)
        msg = mo_info_pb2.GetAllTMORequest()
        resp = await stub.GetAllTMO(msg)
        return [pickle.loads(bytes.fromhex(item)) for item in resp.tmo_info]


async def get_all_tprms_for_special_tmo_id_channel_in(tmo_id: int):
    """Returns all TPRMs data for special tmo_id"""
    async with grpc.aio.insecure_channel(f'{INVENTORY_HOST}:{INVENTORY_GRPC_PORT}') as async_channel:
        stub = mo_info_pb2_grpc.InformerStub(async_channel)
        msg = mo_info_pb2.RequestGetAllTPRMSByTMOId(tmo_id=tmo_id)
        grpc_response = stub.GetAllTPRMSByTMOId(msg)
        result = []
        async for grpc_chunk in grpc_response:
            result.extend([pickle.loads(bytes.fromhex(item)) for item in grpc_chunk.tprms_data])
        return result
