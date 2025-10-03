from logging import getLogger

from application.importer.dto import OTImportRequestDTO
from application.importer.exceptions import (
    ObjectTemplateImportApplicationException,
)
from domain.importer.validate_service import TemplateImportValidationService


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
    def __init__(self, validation_service: TemplateImportValidationService):
        self._validation_service = validation_service
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(self, request: OTImportRequestDTO):
        try:
            self.logger.info(request)
            validation_result = (
                await self._validation_service.validate_excel_import(
                    excel_data=request.file_data,
                    owner=request.owner,
                )
            )

            self.logger.info(
                f"Validation completed: valid={validation_result.is_valid}, "
                f"errors={len(validation_result.errors)}, "
                f"warnings={len(validation_result.warnings)}"
            )

            return []
        except ObjectTemplateImportApplicationException as ex:
            self.logger.error(ex)
            raise
        except Exception as ex:
            self.logger.error(ex)
            raise ObjectTemplateImportApplicationException(
                status_code=422, detail="Application Error."
            )
