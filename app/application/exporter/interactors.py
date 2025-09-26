from logging import getLogger

from application.exporter.dto import TemplateExportResponseDTO
from application.exporter.exceptions import (
    ObjectTemplateExportApplicationException,
)
from application.template_object.read.exceptions import (
    TemplateObjectReaderApplicationException,
)
from domain.exporter.enrich_service import OTEnrichService
from domain.exporter.export_service import ObjectTemplateExportService
from domain.exporter.query import DataFormatter


class ObjectTemplateExportInteractor(object):
    def __init__(
        self,
        ot_exporter: ObjectTemplateExportService,
        data_formatter: DataFormatter,
        enricher: OTEnrichService,
    ):
        self._ot_exporter = ot_exporter
        self._data_formatter = data_formatter
        self._enricher = enricher
        self.logger = getLogger(self.__class__.__name__)

    async def __call__(self, request):
        try:
            export_data = await self._ot_exporter.export(request.template_ids)
            enriched_data = await self._enricher.enrich_to_export(export_data)

            excel_buffer = self._data_formatter.format_to_excel(enriched_data)

            filename = f"object_template_export_{enriched_data.exported_at:%Y-%m-%d-%H-%M}.xlsx"
            return TemplateExportResponseDTO(
                excel_file=excel_buffer,
                filename=filename,
            )

        except ObjectTemplateExportApplicationException as ex:
            self.logger.error(ex)
            raise
        except Exception as ex:
            self.logger.error(ex)
            raise TemplateObjectReaderApplicationException(
                status_code=422, detail="Application Error."
            )
