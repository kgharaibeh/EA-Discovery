from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.models.asset import AssetType, AssetStatus, OSFamily


class AssetResponse(BaseModel):
    id: str
    hostname: str
    ip_addresses: list[str]
    asset_type: AssetType
    status: AssetStatus
    os_family: OSFamily
    os_version: str | None

    discovered_at: datetime
    last_scanned: datetime
    scan_id: str
    source: str

    open_ports: list[dict[str, Any]]
    installed_software: list[dict[str, Any]]
    running_services: list[dict[str, Any]]
    listening_services: list[dict[str, Any]]

    app_server_type: str | None
    deployed_artifacts: list[dict[str, Any]]

    db_engine: str | None
    db_version: str | None
    databases: list[dict[str, Any]]

    config_files: list[dict[str, Any]]
    data_classifications: list[dict[str, Any]]

    business_context: dict[str, Any] | None
    human_verified: bool
    tags: list[str]
    custom_attributes: dict[str, Any]


class AssetUpdate(BaseModel):
    tags: list[str] | None = None
    business_context: dict[str, Any] | None = None
    custom_attributes: dict[str, Any] | None = None
    human_verified: bool | None = None
    status: AssetStatus | None = None


class AssetListResponse(BaseModel):
    items: list[AssetResponse]
    total: int
    page: int
    page_size: int
