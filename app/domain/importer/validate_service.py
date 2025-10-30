from datetime import datetime, timezone
from io import BytesIO
from logging import getLogger

import pandas as pd

from domain.common.exceptions import DomainException
from domain.importer.vo.import_validation_result import ImportValidationResult
from domain.importer.vo.validation_error import ValidationErrorMessage
from domain.importer.vo.validation_result import ValidationResult
from domain.template.query import TemplateReader
from domain.tmo_validation.query import TMOReader
from domain.tprm_validation.query import TPRMReader
from domain.tprm_validation.vo.validation_filter import (
    ParameterValidationFilter,
)


class TemplateImportValidationService(object):
    REQUIRED_SHEETS = ["Templates", "Objects", "Parameters"]

    REQUIRED_TEMPLATE_COLUMNS = [
        "name",
        "object_type_name",
        "valid",
    ]
    REQUIRED_OBJECT_COLUMNS = [
        "template_name",
        "parent_object_name",
        "object_type_name",
        "required",
        "valid",
    ]
    REQUIRED_PARAMETER_COLUMNS = [
        "template_object_type_name",
        "parameter_type_name",
        "value",
        "constraint",
        "val_type",
        "required",
        "valid",
    ]

    def __init__(
        self,
        t_reader: TemplateReader,
        tprm_reader: TPRMReader,
        tmo_reader: TMOReader,
    ):
        self._t_reader = t_reader
        self._tmo_repo = tmo_reader
        self._tprm_repo = tprm_reader
        self.logger = getLogger(self.__class__.__name__)

    async def validate_excel_import(
        self, excel_data: bytes
    ) -> ImportValidationResult:
        result = ValidationResult()
        sheets_data = self._validate_excel_structure(excel_data, result)
        if sheets_data:
            self._validate_sheets_content(sheets_data, result)
            self._validate_correct_link_names(sheets_data, result)
            existed_tmo = await self._validate_inventory_tmo(
                sheets_data, result
            )
            await self._validate_inventory_tprm(
                sheets_data.get("Parameters", pd.DataFrame()),
                result,
                existed_tmo,
            )
            return ImportValidationResult(
                templates=sheets_data.get("Templates", pd.DataFrame()),
                template_objects=sheets_data.get("Objects", pd.DataFrame()),
                template_parameters=sheets_data.get(
                    "Parameters", pd.DataFrame()
                ),
                validated_at=datetime.now(tz=timezone.utc),
                result=result,
            )
        else:
            raise DomainException(
                status_code=422,
                detail="Missing sheet(s) in the validation file.",
            )

    def _validate_excel_structure(
        self, excel_data: bytes, result: ValidationResult
    ) -> dict:
        try:
            excel_file = pd.ExcelFile(BytesIO(excel_data))
            sheets_data = {}

            missing_sheets = set(self.REQUIRED_SHEETS) - set(
                excel_file.sheet_names
            )
            if missing_sheets:
                result.add_error(
                    ValidationErrorMessage(
                        message=f"Missing sheets: {missing_sheets}",
                        sheet_name=" ".join(missing_sheets),
                    )
                )
                return {}
            for sheet_name in self.REQUIRED_SHEETS:
                try:
                    df = pd.read_excel(excel_file, sheet_name=sheet_name)
                    if df.empty:
                        result.add_error(
                            ValidationErrorMessage(
                                sheet_name=sheet_name,
                                message=f"Missing sheet: {sheet_name}",
                            )
                        )
                    sheets_data[sheet_name] = df
                except Exception as ex:
                    result.add_error(
                        ValidationErrorMessage(
                            message=str(ex), sheet_name=sheet_name
                        )
                    )

            return sheets_data

        except Exception:
            return {}

    def _validate_sheets_content(
        self, sheets_data: dict, result: ValidationResult
    ):
        self._validate_templates_sheet(sheets_data["Templates"], result)
        self._validate_objects_sheet(sheets_data["Objects"], result)
        self._validate_parameters_sheet(sheets_data["Parameters"], result)

    def _validate_templates_sheet(
        self, df: pd.DataFrame, result: ValidationResult
    ):
        missing_columns = set(self.REQUIRED_TEMPLATE_COLUMNS) - set(df.columns)
        if missing_columns:
            result.add_error(
                ValidationErrorMessage(
                    message=f"Missing columns: {missing_columns}",
                    sheet_name="Templates",
                )
            )
            return

        # Validate empty values
        has_empty = df.isnull().any(axis=1)
        empty_rows = df.index[has_empty].tolist()
        if empty_rows:
            for r in empty_rows:
                result.add_error(
                    ValidationErrorMessage(
                        message="Missing required data in row(s).",
                        sheet_name="Templates",
                        row=r,
                    )
                )

    def _validate_objects_sheet(
        self, df: pd.DataFrame, result: ValidationResult
    ):
        missing_columns = set(self.REQUIRED_OBJECT_COLUMNS) - set(df.columns)
        non_empty_columns = [
            "template_name",
            "object_type_name",
            "required",
            "valid",
        ]
        if missing_columns:
            result.add_error(
                ValidationErrorMessage(
                    message=f"Missing columns: {missing_columns}",
                    sheet_name="Objects",
                )
            )
            return

        # Validate empty values
        has_empty = df[non_empty_columns].isnull().any(axis=1)
        empty_rows = df[non_empty_columns].index[has_empty].tolist()
        if empty_rows:
            result.add_error(
                ValidationErrorMessage(
                    message="Missing required data in row(s).",
                    sheet_name="Objects",
                    column=" ".join(map(str, empty_rows)),
                )
            )

    def _validate_parameters_sheet(
        self, df: pd.DataFrame, result: ValidationResult
    ):
        missing_columns = set(self.REQUIRED_PARAMETER_COLUMNS) - set(df.columns)
        non_empty_columns = [
            "template_object_type_name",
            "parameter_type_name",
            "value",
            "val_type",
            "required",
            "valid",
        ]
        if missing_columns:
            result.add_error(
                ValidationErrorMessage(
                    message=f"Missing columns: {missing_columns}",
                    sheet_name="Parameters",
                )
            )
            return

        # Validate empty values
        has_empty = df[non_empty_columns].isnull().any(axis=1)
        empty_rows = df[non_empty_columns].index[has_empty].tolist()
        if empty_rows:
            result.add_error(
                ValidationErrorMessage(
                    message="Missing required data in row(s).",
                    sheet_name="Parameters",
                    column=" ".join(map(str, empty_rows)),
                )
            )

    def _validate_correct_link_names(
        self,
        sheets_data: dict,
        result: ValidationResult,
    ):
        templates_df = sheets_data.get("Templates", pd.DataFrame())
        objects_df = sheets_data.get("Objects", pd.DataFrame())
        parameters_df = sheets_data.get("Parameters", pd.DataFrame())

        self._validate_template_references(templates_df, objects_df, result)
        self._validate_object_type_references(objects_df, parameters_df, result)
        self._validate_parent_object_references(objects_df, result)

    @staticmethod
    def _validate_template_references(
        templates_df: pd.DataFrame,
        objects_df: pd.DataFrame,
        result: ValidationResult,
    ):
        template_names = set(templates_df["name"].dropna().astype(str))
        object_template_refs = objects_df["template_name"].dropna().astype(str)
        for idx, template_ref in object_template_refs.items():
            if template_ref not in template_names:
                row_num = idx + 1
                result.add_error(
                    ValidationErrorMessage(
                        message=f"Object references non-existent template_name: '{template_ref}'",
                        sheet_name="Objects",
                        row=row_num,
                        column="template_name",
                    )
                )

    @staticmethod
    def _validate_object_type_references(
        objects_df: pd.DataFrame,
        parameters_df: pd.DataFrame,
        result: ValidationResult,
    ):
        object_types = set(objects_df["object_type_name"].dropna().astype(str))
        parameter_object_refs = (
            parameters_df["template_object_type_name"].dropna().astype(str)
        )
        for idx, object_type_ref in parameter_object_refs.items():
            if object_type_ref not in object_types:
                row_num = idx + 1
                result.add_error(
                    ValidationErrorMessage(
                        message=f"Parameter references non-existent object type: '{object_type_ref}'",
                        sheet_name="Parameters",
                        row=row_num,
                        column="template_object_type_name",
                    )
                )

    @staticmethod
    def _validate_parent_object_references(
        objects_df: pd.DataFrame, result: ValidationResult
    ):
        for template_name, template_objects in objects_df.groupby(
            "template_name"
        ):
            object_types_in_template = set(
                template_objects["object_type_name"].dropna().astype(str)
            )
            for row_num_0, (idx, row) in enumerate(
                template_objects.iterrows(), start=1
            ):
                parent_name = row["parent_object_name"]
                if pd.isna(parent_name) or str(parent_name).strip() == "":
                    continue
                parent_name = str(parent_name)
                if parent_name not in object_types_in_template:
                    row_num = row_num_0 + 1
                    result.add_error(
                        ValidationErrorMessage(
                            message=f"Object references "
                            f"non-existent parent '{parent_name}' in template '{template_name}'",
                            sheet_name="Objects",
                            row=row_num,
                            column="parent_object_name",
                        )
                    )

    async def _validate_inventory_tmo(
        self,
        sheets_data: dict,
        result: ValidationResult,
    ) -> list[int]:
        full_data = await self._tmo_repo.get_all_tmo_data()
        tmo_name_with_tmo_id: dict[str, tuple[int, int]] = dict()
        tmo_id_tmo_name: dict[int, str] = dict()
        output: set[int] = set()
        mapping_for_parameters = dict()
        for tmo in full_data:
            tmo_name_with_tmo_id[tmo.name] = (tmo.id, tmo.parent_id)
            tmo_id_tmo_name[tmo.id] = tmo.name
        if not tmo_name_with_tmo_id or not tmo_id_tmo_name:
            raise DomainException(status_code=422, detail="No tmo name found.")

        # validate  existence tmo
        templates_df = sheets_data.get("Templates", pd.DataFrame())
        objects_df = sheets_data.get("Objects", pd.DataFrame())
        parameters_df = sheets_data.get("Parameters", pd.DataFrame())
        t_tmo_names = set(templates_df["object_type_name"].astype(str))
        to_tmo_names = set(objects_df["object_type_name"].astype(str))
        parent_to_tmo_names = set(
            objects_df["parent_object_name"].dropna().astype(str)
        )
        all_tmo_names = t_tmo_names | to_tmo_names | parent_to_tmo_names
        not_existed_tmo_names = all_tmo_names - set(tmo_name_with_tmo_id.keys())
        if not_existed_tmo_names:
            result.add_error(
                ValidationErrorMessage(
                    message=f"Not existed tmo names: {not_existed_tmo_names}",
                    sheet_name="Objects",
                )
            )
        # Check parents link
        for idx, el in objects_df.iterrows():  # type: int, dict
            row_num = idx + 1
            tmo_tuple = tmo_name_with_tmo_id.get(el["object_type_name"])
            if tmo_tuple is not None:
                output.add(tmo_tuple[0])
                mapping_for_parameters[el["object_type_name"]] = tmo_tuple[0]
            if not pd.isna(el["parent_object_name"]):
                p_tmo_id, _ = tmo_name_with_tmo_id.get(
                    el["parent_object_name"], (0, 0)
                )
                if (
                    p_tmo_id
                    and parent_to_tmo_names
                    and tmo_id_tmo_name.get(p_tmo_id, None)
                ):
                    continue
                else:
                    result.add_error(
                        ValidationErrorMessage(
                            message="Incorrect parent tmo name",
                            sheet_name="Objects",
                            row=row_num,
                            column="parent_object_name",
                        )
                    )
        parameters_df["template_object_id"] = parameters_df[
            "template_object_type_name"
        ].map(mapping_for_parameters)
        return list(output)

    async def _validate_inventory_tprm(
        self,
        parameters_df: pd.DataFrame,
        result: ValidationResult,
        tmo_ids: list[int],
    ):
        for tmo_id in tmo_ids:
            tmo_filter = ParameterValidationFilter(tmo_id=tmo_id)
            tprm_data = await self._tprm_repo.get_all_tprms_by_tmo_id(
                tmo_filter
            )
            filtered_df = parameters_df[
                parameters_df["template_object_id"] == tmo_id
            ][["parameter_type_name", "val_type"]]
            expected_tprm = {el.name: el.val_type for el in tprm_data.values()}
            match_mask = filtered_df["val_type"] == filtered_df[
                "parameter_type_name"
            ].map(expected_tprm)
            filtered_df["matches_expected"] = match_mask
            mismatches = filtered_df[~match_mask]
            if not mismatches.empty:
                result.add_error(
                    ValidationErrorMessage(
                        message=f"Incorrect parameter value types: {mismatches}",
                        sheet_name="Parameters",
                    )
                )
