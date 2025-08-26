from dataclasses import dataclass

from domain.common.exceptions import InvalidValueError
from domain.common.value_object import ValueObject


@dataclass(frozen=True, slots=True)
class ObjectTypeId(ValueObject[int]):
    def _validate(self):
        if self.value < 1:
            raise InvalidValueError(
                status_code=422,
                detail="Object type id (tmo_id) must be positive.",
            )
