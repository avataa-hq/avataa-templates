from dataclasses import fields
from typing import Type

from sqlalchemy import Select

from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_parameter.aggregate import (
    TemplateParameterAggregate,
)
from domain.template_parameter.vo.parameter_type_id import ParameterTypeId
from domain.template_parameter.vo.template_parameter_exists import (
    TemplateParameterExists,
)
from domain.template_parameter.vo.template_parameter_filter import (
    TemplateParameterFilter,
)
from models import TemplateParameter


def template_parameter_filter_to_sql_query(
    vo: TemplateParameterFilter,
    model: Type,
    query: Select[tuple[TemplateParameter]],
) -> Select[tuple[TemplateParameter]]:
    clauses = []
    exclude_fields = ["limit", "offset"]
    for f in fields(vo):
        if f.name not in exclude_fields:
            value = getattr(vo, f.name)
            if value is not None:
                clauses.append(getattr(model, f.name) == value)
    query.limit(vo.limit)
    query.offset(vo.offset)
    return query.where(*clauses)


def template_parameter_exists_to_sql_query(
    vo: TemplateParameterExists,
    model: Type,
    query: Select[tuple[TemplateParameter]],
):
    clauses = []
    for f in fields(vo):
        value = getattr(vo, f.name)
        if isinstance(value, list):
            clauses.append(
                getattr(model, f.name).in_([el.to_raw() for el in value])
            )
        elif value is not None:
            clauses.append(getattr(model, f.name) == value.to_raw())
    return query.where(*clauses)


def sql_to_domain(db_el: TemplateParameter) -> TemplateParameterAggregate:
    return TemplateParameterAggregate(
        id=db_el.id,
        template_object_id=TemplateObjectId(db_el.template_object_id),
        parameter_type_id=ParameterTypeId(db_el.parameter_type_id),
        value=db_el.value,
        constraint=db_el.constraint,
        required=db_el.required,
        val_type=db_el.val_type,
        valid=db_el.valid,
    )
