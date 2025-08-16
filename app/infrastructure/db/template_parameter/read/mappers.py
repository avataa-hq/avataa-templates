from typing import Type

from sqlalchemy import Select

from domain.template_parameter.template_parameter import (
    TemplateParameterAggregate,
)
from domain.template_parameter.vo.parameter_type_id import ParameterTypeId
from domain.template_parameter.vo.template_object_id import TemplateObjectId
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
    for field in vo.__slots__:
        if field not in exclude_fields:
            value = getattr(vo, field)
            if value is not None:
                clauses.append(getattr(model, field) == value)
    query.limit(vo.limit)
    query.offset(vo.offset)
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
