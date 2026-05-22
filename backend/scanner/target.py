from dataclasses import dataclass, field


@dataclass
class ScanTarget:
    host: str
    port: int = 22
    credential_id: str = ""
    os_family: str = "unknown"
    metadata: dict = field(default_factory=dict)
