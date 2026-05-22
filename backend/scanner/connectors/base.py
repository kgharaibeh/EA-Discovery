from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class CommandResult:
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: float = 0.0


class AbstractConnector(ABC):
    @abstractmethod
    async def connect(self, host: str, port: int, credentials: dict) -> None: ...

    @abstractmethod
    async def execute(self, command: str, timeout: int = 30) -> CommandResult: ...

    @abstractmethod
    async def read_file(self, path: str, max_bytes: int = 1_048_576) -> str: ...

    @abstractmethod
    async def list_directory(self, path: str) -> list[dict]: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    def is_connected(self) -> bool: ...
