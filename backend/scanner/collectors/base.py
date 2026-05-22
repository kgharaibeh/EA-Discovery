from abc import ABC, abstractmethod

from scanner.connectors.base import AbstractConnector


class AbstractCollector(ABC):
    @abstractmethod
    async def collect(self, connector: AbstractConnector, os_family: str) -> dict: ...

    @abstractmethod
    def supports_os(self, os_family: str) -> bool: ...
