from typing import Protocol

from domain.template.aggregate import TemplateAggregate
from domain.template.vo.template_filter import TemplateFilter


class TemplateReader(Protocol):
    async def get_all_templates(self) -> None: ...

    async def get_template_by_filter(
        self, db_filter: TemplateFilter
    ) -> list[TemplateAggregate]: ...
