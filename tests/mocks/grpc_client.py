from unittest.mock import AsyncMock

import grpc


class MockGrpcClient:
    def __init__(self):
        self.get_all_tmo_data = AsyncMock()
        self.get_all_tprms_for_tmo = AsyncMock()

        self.get_all_tmo_data.return_value = (
            self._default_tmo_data()
        )
        self.get_all_tprms_for_tmo.return_value = self._default_tprm_data()

    def _default_tmo_data(self) -> list[dict]:
        return [
            {
                "id": 1,
                "p_id": None,
            },  # Корневой объект
            {
                "id": 2,
                "p_id": 1,
            },  # Дочерний объект
            {
                "id": 3,
                "p_id": 1,
            },  # Еще один дочерний объект
        ]

    def _default_tprm_data(self) -> list[dict]:
        return [
            {
                "id": 1,
                "val_type": "string",
                "constraint": None,
                "required": True,
                "multiple": False,
            },
            {
                "id": 2,
                "val_type": "number",
                "constraint": ">=0",
                "required": False,
                "multiple": True,
            },
        ]

    def set_response(self, method: str, response):
        getattr(
            self, method
        ).return_value = response

    def set_error(
        self, method: str, error: grpc.RpcError
    ):
        getattr(self, method).side_effect = error
