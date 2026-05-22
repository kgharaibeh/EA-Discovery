from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AssetType(str, Enum):
    SERVER = "server"
    DATABASE = "database"
    APPLICATION = "application"
    APP_SERVER = "app_server"
    WEB_SERVICE = "web_service"
    API_ENDPOINT = "api_endpoint"
    MIDDLEWARE = "middleware"
    LOAD_BALANCER = "load_balancer"
    FILE_SHARE = "file_share"


class AssetStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DECOMMISSIONED = "decommissioned"
    UNKNOWN = "unknown"


class OSFamily(str, Enum):
    LINUX = "linux"
    WINDOWS = "windows"
    AIX = "aix"
    SOLARIS = "solaris"
    UNKNOWN = "unknown"


class Asset(BaseModel):
    id: str = Field(alias="_id")
    hostname: str
    ip_addresses: list[str] = []
    asset_type: AssetType = AssetType.SERVER
    status: AssetStatus = AssetStatus.ACTIVE
    os_family: OSFamily = OSFamily.UNKNOWN
    os_version: str | None = None

    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    last_scanned: datetime = Field(default_factory=datetime.utcnow)
    scan_id: str = ""
    source: str = "infrastructure_scan"

    open_ports: list[dict[str, Any]] = []
    installed_software: list[dict[str, Any]] = []
    running_services: list[dict[str, Any]] = []
    listening_services: list[dict[str, Any]] = []

    app_server_type: str | None = None
    deployed_artifacts: list[dict[str, Any]] = []

    db_engine: str | None = None
    db_version: str | None = None
    databases: list[dict[str, Any]] = []

    config_files: list[dict[str, Any]] = []
    data_classifications: list[dict[str, Any]] = []

    business_context: dict[str, Any] | None = None
    ai_suggestions: list[str] = []
    human_verified: bool = False

    tags: list[str] = []
    custom_attributes: dict[str, Any] = {}

    model_config = {"populate_by_name": True}
