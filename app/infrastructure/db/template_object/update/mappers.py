from domain.template_object.aggregate import TemplateObjectAggregate
from models import TemplateObject


def domain_to_sql(aggr: TemplateObjectAggregate) -> TemplateObject:
    output = TemplateObject(
        template_id=aggr.template_id.to_raw(),
        object_type_id=aggr.object_type_id.to_raw(),
        required=aggr.required,
        valid=aggr.valid,
        parent_object_id=aggr.parent_object_id,
    )
    output.id = aggr.id.to_raw()
    return output


def domain_to_dict(aggr: TemplateObjectAggregate) -> dict:
    output = {
        "id": aggr.id.to_raw(),
        "template_id": aggr.template_id.to_raw(),
        "object_type_id": aggr.object_type_id.to_raw(),
        "required": aggr.required,
        "valid": aggr.valid,
        "parent_object_id": aggr.parent_object_id,
    }
    return output
