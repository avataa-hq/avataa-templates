from typing import Protocol


class TPRMReader(Protocol):
    async def get_all_tprms_by_tmo_id(self, tmo_id: int) -> dict: ...
