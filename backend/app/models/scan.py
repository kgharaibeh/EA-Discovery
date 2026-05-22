from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ScanStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PARTIAL = "partial"


class ScanType(str, Enum):
    FULL = "full"
    INFRASTRUCTURE = "infrastructure"
    TRAFFIC = "traffic"
    FILESYSTEM = "filesystem"
    IDENTITY = "identity"
    RESCAN = "rescan"


class Scan(BaseModel):
    id: str = Field(alias="_id")
    scan_type: ScanType = ScanType.FULL
    status: ScanStatus = ScanStatus.PENDING
    targets: list[dict[str, Any]] = []
    scope: dict[str, Any] = {}

    total_targets: int = 0
    completed_targets: int = 0
    failed_targets: list[dict[str, Any]] = []

    assets_discovered: int = 0
    relationships_discovered: int = 0
    new_assets: int = 0
    updated_assets: int = 0

    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: datetime | None = None
    completed_at: datetime | None = None

    celery_task_id: str | None = None
    initiated_by: str = "manual"
    schedule_id: str | None = None

    model_config = {"populate_by_name": True}
