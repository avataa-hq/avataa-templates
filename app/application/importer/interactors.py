from datetime import datetime, timezone
from logging import getLogger

from application.importer.dto import OTImportRequestDTO, OTImportResponseDTO
from application.importer.exceptions import (
    ObjectTemplateImportApplicationException,
)
from domain.common.exceptions import DomainException
from domain.exporter.query import DataFormatter
from domain.importer.enrich_service import OTEnrichErrorService
from domain.importer.validate_service import TemplateImportValidationService
from domain.importer.vo.import_validation_result import ImportValidationResult


class ObjectTemplateImportInteractor(object):
    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(self, request: OTImportRequestDTO):
        try:
            self.logger.info(request)
            return []
        except ObjectTemplateImportApplicationException as ex:
            self.logger.error(ex)
            raise
        except Exception as ex:
            self.logger.error(ex)
            raise ObjectTemplateImportApplicationException(
                status_code=422, detail="Application Error."
            )


class ObjectTemplateImportValidationInteractor(object):
    def __init__(
        self,
        validation_service: TemplateImportValidationService,
        data_formatter: DataFormatter,
        enricher: OTEnrichErrorService,
    ):
        self._validation_service = validation_service
        self._data_formatter = data_formatter
        self._enricher = enricher
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(
        self, request: OTImportRequestDTO
    ) -> OTImportResponseDTO:
        try:
            validation_data: ImportValidationResult = (
                await self._validation_service.validate_excel_import(
                    excel_data=request.file_data,
                )
            )
            self.logger.info(
                f"Validation completed: valid={validation_data.result.is_valid}, "
                f"errors={len(validation_data.result.errors)}, "
                f"errors={validation_data.result.errors}, "
            )
            if validation_data.result.is_valid:
                filename = f"object_template_validation_{datetime.now(tz=timezone.utc):%Y-%m-%d-%H-%M}.xlsx"
                return OTImportResponseDTO(
                    data_file=request.file_data,
                    result=validation_data.result,
                    filename=filename,
                )
            else:
                enriched_data: ImportValidationResult = (
                    self._enricher.enrich_error_to_validate(validation_data)
                )
                excel_buffer = self._data_formatter.format_to_excel_with_errors(
                    enriched_data
                )
                filename = f"object_template_validation_{enriched_data.validated_at:%Y-%m-%d-%H-%M}.xlsx"
                return OTImportResponseDTO(
                    data_file=excel_buffer,
                    result=validation_data.result,
                    filename=filename,
                )
        except DomainException as ex:
            self.logger.error(ex)
            raise ObjectTemplateImportApplicationException(
                status_code=ex.status_code, detail=ex.detail
            )
        except ObjectTemplateImportApplicationException as ex:
            self.logger.error(ex)
            raise
        except Exception as ex:
            self.logger.error(ex)
            raise ObjectTemplateImportApplicationException(
                status_code=422, detail="Application Error."
            )
