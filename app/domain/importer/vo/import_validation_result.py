from dataclasses import dataclass, field

from domain.importer.vo.validation_error import ValidationError


@dataclass
class ValidationResult:
    errors: set[ValidationError] = field(default_factory=set)
    warnings: set[ValidationError] = field(default_factory=set)

    @property
    def is_valid(self) -> bool:
        return not self.errors

    def add_error(self, error: ValidationError) -> None:
        self.errors.add(error)
