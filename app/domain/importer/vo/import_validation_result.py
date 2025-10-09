from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from domain.importer.vo.validation_result import ValidationResult


@dataclass
class ImportValidationResult:
    templates: pd.DataFrame
    template_objects: pd.DataFrame
    template_parameters: pd.DataFrame
    validated_at: datetime
    result: ValidationResult
