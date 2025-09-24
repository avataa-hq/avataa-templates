from logging import getLogger

from domain.shared.query import DataFormatter
from domain.shared.vo.export_data import CompleteOTExportData


class ExcelDataFormatter(DataFormatter):
    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)

    def format_to_excel(self, request: CompleteOTExportData):
        return []
