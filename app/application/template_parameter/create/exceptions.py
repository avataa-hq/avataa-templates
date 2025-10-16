class TemplateParameterCreatorApplicationException(Exception):
    def __init__(self, detail: str, status_code: int):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail

    def __str__(self):
        if self.status_code:
            return f"[Error {self.status_code}]: {self.detail}"
        return self.detail


class TemplateObjectNotFound(TemplateParameterCreatorApplicationException):
    pass


class GrpcInventoryError(TemplateParameterCreatorApplicationException):
    pass


class TPRMNotFoundInInventory(TemplateParameterCreatorApplicationException):
    pass


class RequiredMismatchException(TemplateParameterCreatorApplicationException):
    pass


class InvalidParameterValue(TemplateParameterCreatorApplicationException):
    pass


class ValueConstraintException(TemplateParameterCreatorApplicationException):
    pass


__all__ = [
    "TemplateParameterCreatorApplicationException",
    "TemplateObjectNotFound",
    "GrpcInventoryError",
    "TPRMNotFoundInInventory",
    "RequiredMismatchException",
    "InvalidParameterValue",
    "ValueConstraintException",
]
