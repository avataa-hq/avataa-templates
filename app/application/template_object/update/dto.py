from dataclasses import dataclass

from domain.template_object.aggregate import TemplateObjectAggregate


# From router
@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateObjectDataUpdateRequestDTO:
    template_object_id: int
    required: bool | None = None
    parent_object_id: int | None = None


# From aggregate to router
@dataclass(frozen=True, slots=True, kw_only=True)
class TemplateObjectUpdateDTO:
    id: int
    template_id: int
    object_type_id: int
    required: bool
    valid: bool

    parent_object_id: int | None = None

    @classmethod
    def from_aggregate(
        cls, aggregate: TemplateObjectAggregate
    ) -> "TemplateObjectUpdateDTO":
        return cls(
            id=aggregate.id.to_raw(),
            template_id=aggregate.template_id.to_raw(),
            object_type_id=aggregate.object_type_id.to_raw(),
            required=aggregate.required,
            valid=aggregate.valid,
            parent_object_id=aggregate.parent_object_id,
        )
