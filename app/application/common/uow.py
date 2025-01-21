from abc import ABC, abstractmethod


class UoW(ABC):
    @abstractmethod
    def commit(self):
        raise NotImplementedError

    @abstractmethod
    def flush(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError
