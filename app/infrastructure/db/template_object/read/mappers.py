from typing import Type

from sqlalchemy import Select

from domain.template_object.template_object import TemplateObjectAggregate
from domain.template_object.vo.template_object_filter import (
    TemplateObjectFilter,
)
from models import TemplateObject


def template_object_filter_to_sql_query(
    vo: TemplateObjectFilter, model: Type, query: Select[tuple[TemplateObject]]
) -> Select[tuple[TemplateObject]]:
    clauses = []
    exclude_fields = ["limit", "offset", "depth", "include_parameters"]
    for field in vo.__slots__:
        if field not in exclude_fields:
            value = getattr(vo, field)
            if value is not None:
                clauses.append(getattr(model, field) == value)
    query.limit(vo.limit)
    query.offset(vo.offset)
    return query.where(*clauses)


def sql_to_domain(db_el: TemplateObject) -> TemplateObjectAggregate:
    return TemplateObjectAggregate(
        id=db_el.id,
        template_id=db_el.template_id,
        parent_object_id=db_el.parent_object_id,
        object_type_id=db_el.object_type_id,
        required=db_el.required,
        valid=db_el.valid,
    )
