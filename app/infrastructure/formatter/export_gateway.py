from io import BytesIO
from logging import getLogger

import pandas as pd

from domain.exporter.query import DataFormatter
from domain.exporter.vo.enriched_export_data import (
    CompleteOTEnrichedExportData,
)
from domain.importer.vo.import_validation_result import ImportValidationResult


class ExcelDataFormatter(DataFormatter):
    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)

    def format_to_excel(self, request: CompleteOTEnrichedExportData) -> BytesIO:
        buffer = BytesIO()

        templates_data = [
            {
                "name": t.aggregate.name,
                # "owner": t.aggregate.owner, - set to import
                "object_type_name": t.object_type_name,
                # "creation_date": t.aggregate.creation_date, - set to import
                # "modification_date": t.aggregate.modification_date, - set to import
                "valid": t.aggregate.valid,
                # "version": t.aggregate.version,  -  set to 1 on import
            }
            for t in request.templates
        ]

        objects_data = [
            {
                "template_name": to.template_name,
                "parent_object_name": to.parent_object_name,
                "object_type_name": to.object_type_name,
                "required": to.aggregate.required,
                "valid": to.aggregate.valid,
            }
            for to in request.template_objects
        ]
        parameters_data = [
            {
                "template_object_type_name": p.template_object_type_name,
                "parameter_type_name": p.parameter_type_name,
                "value": p.aggregate.value,
                "constraint": p.aggregate.constraint,
                "val_type": p.aggregate.val_type,
                "required": p.aggregate.required,
                "valid": p.aggregate.valid,
            }
            for p in request.template_parameters
        ]

        templates_df = pd.DataFrame(templates_data)
        objects_df = pd.DataFrame(objects_data)
        parameters_df = pd.DataFrame(parameters_data)

        with pd.ExcelWriter(buffer, mode="w", engine="xlsxwriter") as writer:
            templates_df.to_excel(writer, sheet_name="Templates", index=False)
            objects_df.to_excel(writer, sheet_name="Objects", index=False)
            parameters_df.to_excel(writer, sheet_name="Parameters", index=False)

        buffer.seek(0)
        return buffer

    def format_to_excel_with_errors(
        self, request: ImportValidationResult
    ) -> bytes:
        buffer = BytesIO()

        with pd.ExcelWriter(buffer, mode="w", engine="xlsxwriter") as writer:
            request.templates.to_excel(
                writer, sheet_name="Templates", index=False
            )
            request.template_objects.to_excel(
                writer, sheet_name="Objects", index=False
            )
            request.template_parameters.to_excel(
                writer, sheet_name="Parameters", index=False
            )

        buffer.seek(0)
        return buffer.getvalue()
