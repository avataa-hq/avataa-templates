from logging import getLogger

import pandas as pd

from domain.template.query import TemplateReader


class TemplateImportValidationService(object):
    REQUIRED_SHEETS = ["Templates", "Objects", "Parameters"]

    REQUIRED_TEMPLATE_COLUMNS = [
        "name",
        "owner",
        "object_type_name",
        "valid",
        "version",
    ]
    REQUIRED_OBJECT_COLUMNS = [
        "template_reference",
        "object_type_name",
        "required",
        "valid",
    ]
    REQUIRED_PARAMETER_COLUMNS = [
        "object_reference",
        "parameter_type_name",
        "val_type",
        "required",
        "valid",
    ]

    def __init__(
        self,
        template_reader: TemplateReader,
    ):
        self._template_reader = template_reader
        self.logger = getLogger(self.__class__.__name__)

    async def validate_excel_import(self, excel_data: bytes, owner: str):
        try:
            sheets_data = await self._validate_excel_structure(excel_data)

            await self._validate_sheets_content(sheets_data)

            await self._validate_business_rules(sheets_data, owner)

            await self._validate_external_dependencies(sheets_data)

        except Exception as ex:
            self.logger.error(f"Validation exception: {ex}")

        return []

    async def _validate_excel_structure(self, excel_data: bytes):
        self.logger.debug(excel_data)
        return {}

    async def _validate_sheets_content(self, sheets_data: dict): ...

    async def _validate_templates_sheet(self, df: pd.DataFrame): ...

    async def _validate_objects_sheet(self, df: pd.DataFrame): ...

    async def _validate_parameters_sheet(self, df: pd.DataFrame): ...

    async def _validate_business_rules(self, sheets_data: dict, owner: str): ...

    async def _validate_external_dependencies(self, sheets_data: dict): ...
