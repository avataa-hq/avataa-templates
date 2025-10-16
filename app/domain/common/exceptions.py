class DomainException(Exception):
    def __init__(self, detail, status_code=None):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail

    def __str__(self):
        if self.status_code:
            return f"[Error {self.status_code}]: {self.detail}"
        return self.detail


class InvalidValueError(DomainException):
    pass


class EmptyValueError(DomainException):
    pass


class ConstraintViolationError(DomainException):
    pass


class RequiredParameterError(DomainException):
    pass


__all__ = [
    "InvalidValueError",
    "EmptyValueError",
    "ConstraintViolationError",
    "RequiredParameterError",
]
