from dataclasses import dataclass


# From router
@dataclass
class OTExportRequestDTO:
    template_ids: list[int]
