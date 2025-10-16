from domain.shared.vo.object_type_id import ObjectTypeId
from domain.shared.vo.template_id import TemplateId
from domain.template.aggregate import TemplateAggregate
from models import Template


def domain_to_sql(aggr: TemplateAggregate) -> Template:
    output = Template(
        name=aggr.name,
        owner=aggr.owner,
        object_type_id=aggr.object_type_id.to_raw(),
        version=aggr.version,
        valid=aggr.valid,
    )
    output.id = aggr.id.to_raw()
    return output


def domain_to_dict(aggr: TemplateAggregate) -> dict:
    output = {
        "id": aggr.id.to_raw(),
        "name": aggr.name,
        "owner": aggr.owner,
        "object_type_id": aggr.object_type_id.to_raw(),
        "version": aggr.version,
        "valid": aggr.valid,
    }
    return output


def sql_to_domain(db_model: Template) -> TemplateAggregate:
    return TemplateAggregate(
        id=TemplateId(db_model.id),
        name=db_model.name,
        owner=db_model.owner,
        object_type_id=ObjectTypeId(db_model.object_type_id),
        creation_date=db_model.creation_date,
        modification_date=db_model.modification_date,
        valid=db_model.valid,
        version=db_model.version,
    )
