from typing import Type

from sqlalchemy import Select

from domain.template.template import TemplateAggregate
from domain.template.vo.template_filter import TemplateFilter
from models import Template


def template_to_sql_query(
    vo: TemplateFilter, model: Type, query: Select[tuple[Template]]
) -> Select[tuple[Template]]:
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


def postgres_to_domain(template: Template) -> TemplateAggregate:
    return TemplateAggregate(
        id=template.id,
        name=template.name,
        owner=template.owner,
        object_type_id=template.object_type_id,
        creation_date=template.creation_date,
        modification_date=template.modification_date,
        valid=template.valid,
        version=template.version,
    )
