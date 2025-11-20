from domain.shared.vo.object_type_id import ObjectTypeId
from domain.shared.vo.template_id import TemplateId
from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_object.aggregate import TemplateObjectAggregate
from models import TemplateObject


def sql_to_domain(db_el: TemplateObject) -> TemplateObjectAggregate:
    return TemplateObjectAggregate(
        id=TemplateObjectId(db_el.id),
        template_id=TemplateId(db_el.template_id),
        object_type_id=ObjectTypeId(db_el.object_type_id),
        required=db_el.required,
        valid=db_el.valid,
    )
