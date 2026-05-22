from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DriftEvent(BaseModel):
    id: str = Field(alias="_id")
    asset_id: str
    scan_id: str
    previous_scan_id: str = ""

    drift_type: str = ""
    field_path: str = ""
    previous_value: Any = None
    current_value: Any = None

    severity: str = "info"
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged: bool = False

    model_config = {"populate_by_name": True}
