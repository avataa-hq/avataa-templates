from typing_extensions import (
    Protocol,
    runtime_checkable,
)


@runtime_checkable
class KafkaMSGProtocol(Protocol):
    def topic(self) -> str: ...

    def key(self) -> str: ...

    def value(self) -> str: ...
