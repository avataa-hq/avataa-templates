from logging import getLogger

import pandas as pd

from domain.importer.vo.import_validation_result import ImportValidationResult


class OTEnrichErrorService(object):
    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)

    def enrich_error_to_validate(
        self, request: ImportValidationResult
    ) -> ImportValidationResult:
        # Add errors to pd
        request.templates["error"] = pd.Series(dtype="string")
        request.template_objects["error"] = pd.Series(dtype="string")
        request.template_parameters["error"] = pd.Series(dtype="string")
        for error in request.result.errors:
            self.logger.error(error)
            match error.sheet_name:
                case "Templates":
                    request.templates.loc[error.row, "error"] = error.message
                case "Objects":
                    if error.row:
                        request.template_parameters.loc[
                            error.row - 1, "error"
                        ] = f"{error.message}: {error.column}"
                case "Parameters":
                    if error.row:
                        request.template_parameters.loc[
                            error.row - 1, "error"
                        ] = f"{error.message}: {error.column}"

        return request
