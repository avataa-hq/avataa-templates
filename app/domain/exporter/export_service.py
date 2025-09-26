from datetime import datetime, timezone
from logging import getLogger

from domain.common.exceptions import DomainException
from domain.exporter.vo.export_data import CompleteOTExportData
from domain.template.query import TemplateReader
from domain.template_object.aggregate import TemplateObjectAggregate
from domain.template_object.query import TemplateObjectReader
from domain.template_parameter.aggregate import TemplateParameterAggregate
from domain.template_parameter.query import TemplateParameterReader


class ObjectTemplateExportService(object):
    def __init__(
        self,
        t_reader: TemplateReader,
        to_reader: TemplateObjectReader,
        tp_reader: TemplateParameterReader,
    ):
        self._t_reader = t_reader
        self._to_reader = to_reader
        self._tp_reader = tp_reader
        self.logger = getLogger(self.__class__.__name__)

    async def export(self, template_ids: list[int]) -> CompleteOTExportData:
        to: list[TemplateObjectAggregate] = []
        tp: list[TemplateParameterAggregate] = []
        try:
            templates = await self._t_reader.get_by_ids(template_ids)
            if len(template_ids) != len({t.name for t in templates}):
                raise DomainException(
                    status_code=422,
                    detail="Duplicate names in templates. Export is not possible.",
                )
            if templates:
                to = await self._to_reader.get_by_template_ids(template_ids)
                tp = await self._tp_reader.get_by_template_object_ids(
                    [obj.id.to_raw() for obj in to]
                )

            return CompleteOTExportData(
                templates=templates,
                template_objects=to,
                template_parameters=tp,
                exported_at=datetime.now(tz=timezone.utc),
            )
        except Exception as ex:
            print(ex)
            raise
