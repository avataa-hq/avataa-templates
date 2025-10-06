from logging import getLogger

import pandas as pd

from domain.common.exceptions import DomainException
from domain.importer.vo.import_validation_result import ValidationResult
from domain.importer.vo.validation_error import ValidationError
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
        result = ValidationResult()
        try:
            sheets_data = self._validate_excel_structure(excel_data, result)
            await self._validate_sheets_content(sheets_data, result)
        except Exception as ex:
            self.logger.error(f"Validation exception: {ex}")

        return result

    def _validate_excel_structure(
        self, excel_data: bytes, result: ValidationResult
    ):
        self.logger.debug(excel_data)
        try:
            excel_file = pd.ExcelFile(excel_data)
            sheets_data = {}

            missing_sheets = set(self.REQUIRED_SHEETS) - set(
                excel_file.sheet_names
            )
            if missing_sheets:
                raise DomainException(
                    status_code=422, detail=f"Missing sheets: {missing_sheets}"
                )
            for sheet_name in self.REQUIRED_SHEETS:
                try:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    if df.empty:
                        result.add_error(
                            ValidationError(
                                sheet_name=sheet_name,
                                message=f"Missing sheet: {sheet_name}",
                            )
                        )
                    sheets_data[sheet_name] = df
                except Exception as ex:
                    result.add_error(
                        ValidationError(message=str(ex), sheet_name=sheet_name)
                    )

            return sheets_data

        except Exception as ex:
            result.add_error(ValidationError(message=f"Read error: {ex}"))
            return {}

    async def _validate_sheets_content(
        self, sheets_data: dict, result: ValidationResult
    ): ...
