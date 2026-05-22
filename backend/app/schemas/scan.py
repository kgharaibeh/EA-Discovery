from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.scan import ScanStatus, ScanType


class ScanCreate(BaseModel):
    scan_type: ScanType = ScanType.FULL
    targets: list[dict[str, Any]] = Field(
        ...,
        description="List of targets: [{'host': '10.0.1.1', 'credential_id': 'cred_1'}]",
    )
    scope: dict[str, Any] = Field(
        default={},
        description="Scan scope: subnets, excluded hosts, port ranges",
    )


class ScanResponse(BaseModel):
    id: str
    scan_type: ScanType
    status: ScanStatus
    targets: list[dict[str, Any]]
    scope: dict[str, Any]
    total_targets: int
    completed_targets: int
    failed_targets: list[dict[str, Any]]
    assets_discovered: int
    relationships_discovered: int
    new_assets: int
    updated_assets: int
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None
    celery_task_id: str | None
    initiated_by: str


class ScanListResponse(BaseModel):
    items: list[ScanResponse]
    total: int
    page: int
    page_size: int
