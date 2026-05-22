from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class RawFlow:
    src_ip: str
    src_port: int
    dst_ip: str
    dst_port: int
    protocol: str
    payload_sample: bytes | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    bytes_transferred: int = 0
    method: str | None = None
    path: str | None = None
    status_code: int | None = None
    content_type: str | None = None


class AbstractTrafficPlugin(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    async def capture(
        self,
        connector,
        interface: str,
        duration_seconds: int,
        filter_expr: str | None = None,
    ) -> list[RawFlow]: ...

    @abstractmethod
    async def parse_file(self, file_path: str) -> list[RawFlow]: ...
