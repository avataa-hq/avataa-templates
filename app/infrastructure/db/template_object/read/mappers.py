from dataclasses import fields
from typing import Type, TypeVar

from sqlalchemy import Select

from domain.shared.vo.object_type_id import ObjectTypeId
from domain.shared.vo.template_id import TemplateId
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_object.aggregate import TemplateObjectAggregate
from domain.template_object.vo.template_object_filter import (
    TemplateObjectFilter,
)
from models import TemplateObject

T = TypeVar("T", bound=tuple)


def template_object_filter_to_sql_query(
    vo: TemplateObjectFilter, model: Type, query: Select[T]
) -> Select[T]:
    clauses = []
    exclude_fields = ["limit", "offset", "depth"]
    for f in fields(vo):
        if f.name not in exclude_fields:
            value = getattr(vo, f.name)
            if value is not None:
                clauses.append(getattr(model, f.name) == value)
    query.limit(vo.limit)
    query.offset(vo.offset)
    return query.where(*clauses)


def sql_to_domain(db_el: TemplateObject) -> TemplateObjectAggregate:
    return TemplateObjectAggregate(
        id=TemplateObjectId(db_el.id),
        template_id=TemplateId(db_el.template_id),
        parent_object_id=db_el.parent_object_id,
        object_type_id=ObjectTypeId(db_el.object_type_id),
        required=db_el.required,
        valid=db_el.valid,
    )
