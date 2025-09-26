from logging import getLogger

from domain.exporter.vo.enriched_export_data import CompleteOTEnrichedExportData
from domain.exporter.vo.export_data import CompleteOTExportData
from domain.exporter.vo.exportable_template import ExportableTemplate
from domain.exporter.vo.exportable_template_object import (
    ExportableTemplateObject,
)
from domain.exporter.vo.exportable_template_parameter import (
    ExportableTemplateParameter,
)
from domain.template.aggregate import TemplateAggregate
from domain.template_object.aggregate import TemplateObjectAggregate
from domain.template_parameter.aggregate import TemplateParameterAggregate
from domain.tmo_validation.query import TMOReader
from domain.tprm_validation.query import TPRMReader
from domain.tprm_validation.vo.validation_filter import (
    ParameterValidationFilter,
)


class OTEnrichService(object):
    def __init__(
        self,
        tmo_repo: TMOReader,
        tprm_repo: TPRMReader,
    ) -> None:
        self._tmo_repo = tmo_repo
        self._tprm_repo = tprm_repo
        self.logger = getLogger(self.__class__.__name__)

    async def enrich_to_export(
        self,
        request: CompleteOTExportData,
    ):
        self.logger.info("enrich_to_export")
        # Create maps
        tmo_ids_from_templates = {
            t.object_type_id.to_raw() for t in request.templates
        }
        tmo_ids_from_to = {
            to.object_type_id.to_raw() for to in request.template_objects
        }
        tmo_ids = tmo_ids_from_templates.union(tmo_ids_from_to)
        tprm_ids = {
            tp.parameter_type_id.to_raw() for tp in request.template_parameters
        }

        all_tmo_data = await self._tmo_repo.get_all_tmo_data()
        all_tprm_data = dict()
        for tmo_id in tmo_ids:
            tmo_filter = ParameterValidationFilter(tmo_id=tmo_id)
            all_tprm_data.update(
                await self._tprm_repo.get_all_tprms_by_tmo_id(tmo_filter)
            )

        tmo_map = {
            tmo.id: tmo.name for tmo in all_tmo_data if tmo.id in tmo_ids
        }
        tprm_map = {
            tprm.id: tprm.name
            for tprm in all_tprm_data.values()
            if tprm.id in tprm_ids
        }
        template_mapper = {t.id.to_raw(): t for t in request.templates}

        # enrich template
        exportable_templates = self._create_exportable_templates(
            request.templates, tmo_map
        )

        # enrich template object
        exportable_template_objects = self._create_exportable_template_objects(
            template_mapper,
            {to.id.to_raw(): to for to in request.template_objects},
            tmo_map,
        )

        # enrich template parameter
        exportable_template_parameters = (
            self._create_exportable_template_parameters(
                {
                    to.aggregate.id.to_raw(): to
                    for to in exportable_template_objects
                },
                request.template_parameters,
                tprm_map,
            )
        )

        return CompleteOTEnrichedExportData(
            templates=exportable_templates,
            template_objects=exportable_template_objects,
            template_parameters=exportable_template_parameters,
            exported_at=request.exported_at,
        )

    @staticmethod
    def _create_exportable_templates(
        templates: list[TemplateAggregate], object_types_map: dict[int, str]
    ) -> list[ExportableTemplate]:
        exportable_templates = []
        for t in templates:
            object_type_name = object_types_map.get(
                t.object_type_id.to_raw(),
                f"unknown_tmo_{t.object_type_id.to_raw()}",
            )

            exportable_templates.append(
                ExportableTemplate(
                    aggregate=t, object_type_name=object_type_name
                )
            )

        return exportable_templates

    @staticmethod
    def _create_exportable_template_objects(
        template_mapper: dict[int, TemplateAggregate],
        template_objects: dict[int, TemplateObjectAggregate],
        object_types_map: dict[int, str],
    ) -> list[ExportableTemplateObject]:
        exportable_template_objects = []
        for to_id, to in template_objects.items():
            object_type_name = object_types_map.get(
                to.object_type_id.to_raw(),
                f"unknown_tmo_{to.object_type_id.to_raw()}",
            )
            parent_name = None
            if to.parent_object_id:
                parent_name = object_types_map.get(
                    template_objects[
                        to.parent_object_id
                    ].object_type_id.to_raw(),
                    f"unknown_parent_tmo_{to.parent_object_id}",
                )
            to_to_export = ExportableTemplateObject(
                aggregate=to,
                template_name=template_mapper[to.template_id.to_raw()].name,
                object_type_name=object_type_name,
                parent_object_name=parent_name,
            )
            exportable_template_objects.append(to_to_export)
        return exportable_template_objects

    @staticmethod
    def _create_exportable_template_parameters(
        template_objects_mapper: dict[int, ExportableTemplateObject],
        template_parameters: list[TemplateParameterAggregate],
        parameter_types_map: dict[int, str],
    ) -> list[ExportableTemplateParameter]:
        exportable_template_parameters = []
        for tp in template_parameters:
            parameter_type_name = parameter_types_map.get(
                tp.parameter_type_id.to_raw(),
                f"unknown_tprm_{tp.parameter_type_id.to_raw()}",
            )

            exportable_template_parameters.append(
                ExportableTemplateParameter(
                    aggregate=tp,
                    template_object_type_name=template_objects_mapper[
                        tp.template_object_id.to_raw()
                    ].object_type_name,
                    parameter_type_name=parameter_type_name,
                )
            )

        return exportable_template_parameters
