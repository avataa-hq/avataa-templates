from domain.shared.vo.template_object_id import TemplateObjectId
from domain.template_parameter.aggregate import TemplateParameterAggregate
from domain.template_parameter.vo.parameter_type_id import ParameterTypeId
from models import TemplateParameter


def domain_to_sql(aggr: TemplateParameterAggregate) -> TemplateParameter:
    output = TemplateParameter(
        template_object_id=aggr.template_object_id.to_raw(),
        parameter_type_id=aggr.parameter_type_id.to_raw(),
        value=aggr.value,
        constraint=aggr.constraint,
        val_type=aggr.val_type,
        required=aggr.required,
        valid=aggr.valid,
    )
    output.id = aggr.id
    return output


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
