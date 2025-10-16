class ObjectTemplateImportApplicationException(Exception):
    def __init__(self, detail: str, status_code: int):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail

    def __str__(self):
        if self.status_code:
            return f"[Error {self.status_code}]: {self.detail}"
        return self.detail


__all__ = ["ObjectTemplateImportApplicationException"]
