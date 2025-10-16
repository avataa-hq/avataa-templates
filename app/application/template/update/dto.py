from dataclasses import dataclass

from domain.template.aggregate import TemplateAggregate


# From router
@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateDataUpdateRequestDTO:
    id: int
    name: str
    owner: str
    object_type_id: int


# From aggregate to router
@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateUpdateResponseDTO:
    id: int
    name: str
    owner: str
    object_type_id: int
    valid: bool

    @classmethod
    def from_aggregate(
        cls, aggregate: TemplateAggregate
    ) -> "TemplateUpdateResponseDTO":
        return cls(
            id=aggregate.id.to_raw(),
            name=aggregate.name,
            owner=aggregate.owner,
            object_type_id=aggregate.object_type_id.to_raw(),
            valid=aggregate.valid,
        )
