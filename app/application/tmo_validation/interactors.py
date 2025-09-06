from logging import getLogger

from application.tmo_validation.dto import TemplateObjectValidationRequestDTO
from application.tmo_validation.exceptions import TMOValidationException
from domain.tmo_validation.query import TMOReader


class TMOValidationInteractor(object):
    def __init__(self, repo: TMOReader):
        self._repo = repo
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(self, request: TemplateObjectValidationRequestDTO):
        full_data = await self._repo.get_all_tmo_data()
        checker = {el.id: el.parent_id for el in full_data}
        if request.parent_object_type_id not in checker:
            raise TMOValidationException(
                status_code=404, detail="Parent object type not found."
            )
        expected_parent_id = checker[request.object_type_id]
        if expected_parent_id != request.parent_object_type_id:
            raise TMOValidationException(
                status_code=422, detail="Incorrect parent object type."
            )
