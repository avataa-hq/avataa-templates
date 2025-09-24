from typing import Protocol


class DataFormatter(Protocol):
    def format_to_excel(self, request): ...
