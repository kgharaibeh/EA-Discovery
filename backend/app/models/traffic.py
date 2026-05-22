from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class TrafficCapture(BaseModel):
    id: str = Field(alias="_id")
    scan_id: str = ""
    source_plugin: str = ""
    target_host: str = ""
    capture_duration_seconds: int = 0

    flows: list[dict[str, Any]] = []
    api_endpoints_discovered: list[dict[str, Any]] = []
    captured_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}
