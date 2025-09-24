from logging import getLogger

from application.exporter.exceptions import (
    ObjectTemplateExportApplicationException,
)
from application.template_object.read.exceptions import (
    TemplateObjectReaderApplicationException,
)
from domain.shared.export_service import ObjectTemplateExportService
from domain.shared.query import DataFormatter


class ObjectTemplateExportInteractor(object):
    def __init__(
        self,
        ot_exporter: ObjectTemplateExportService,
        data_formatter: DataFormatter,
    ):
        self._ot_exporter = ot_exporter
        self._data_formatter = data_formatter
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(self, request):
        try:
            export_data = await self._ot_exporter.export(request.template_ids)

            excel_buffer = self._data_formatter.format_to_excel(export_data)
            print(excel_buffer)
            filename = (
                f"templates_export_{len(export_data.templates)}_items.xlsx"
            )
            print(filename)
            return []

        except ObjectTemplateExportApplicationException as ex:
            self.logger.error(ex)
            raise
        except Exception as ex:
            self.logger.error(ex)
            raise TemplateObjectReaderApplicationException(
                status_code=422, detail="Application Error."
            )
