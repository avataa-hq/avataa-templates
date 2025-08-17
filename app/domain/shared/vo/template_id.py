from dataclasses import dataclass

from domain.common.exceptions import IncorrectValueError
from domain.common.value_object import ValueObject


@dataclass(frozen=True, slots=True)
class TemplateId(ValueObject[int]):
    def _validate(self):
        if self.value < 1:
            raise IncorrectValueError(
                status_code=422,
                detail="Template id must be positive.",
            )
