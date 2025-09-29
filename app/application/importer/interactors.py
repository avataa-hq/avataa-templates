from logging import getLogger

from application.importer.dto import OTImportRequestDTO
from application.importer.exceptions import (
    ObjectTemplateImportApplicationException,
)


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
