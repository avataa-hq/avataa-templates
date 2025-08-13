from dataclasses import dataclass
from datetime import datetime


@dataclass
class TemplateAggregate(object):
    id: int
    name: str
    owner: str
    object_type_id: int
    creation_date: datetime
    modification_date: datetime
    valid: bool
    version: int
