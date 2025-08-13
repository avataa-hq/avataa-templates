from domain.template.template import TemplateAggregate
from models import Template


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
