from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Schedule(BaseModel):
    id: str = Field(alias="_id")
    name: str
    cron_expression: str = "0 2 * * *"
    scan_config: dict[str, Any] = {}
    enabled: bool = True
    last_run: datetime | None = None
    next_run: datetime | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}
