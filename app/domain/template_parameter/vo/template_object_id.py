from dataclasses import dataclass

from domain.common.exceptions import IncorrectValueError
from domain.common.value_object import ValueObject


@dataclass(frozen=True, slots=True)
class TemplateObjectId(ValueObject[int]):
    def _validate(self):
        if self.value < 1:
            raise IncorrectValueError(
                status_code=422,
                detail="Template object id must be positive.",
            )
