from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RelationshipType(str, Enum):
    CONNECTS_TO = "connects_to"
    DEPENDS_ON = "depends_on"
    HOSTS = "hosts"
    QUERIES = "queries"
    CALLS_API = "calls_api"
    AUTHENTICATES_VIA = "authenticates_via"
    LOAD_BALANCES = "load_balances"
    READS_FROM = "reads_from"
    WRITES_TO = "writes_to"


class RelationshipSource(str, Enum):
    CONFIG_PARSE = "config_parse"
    NETWORK_CONNECTION = "network_connection"
    TRAFFIC_ANALYSIS = "traffic_analysis"
    AI_INFERRED = "ai_inferred"
    MANUAL = "manual"


class Relationship(BaseModel):
    id: str = Field(alias="_id")
    source_asset_id: str
    target_asset_id: str
    relationship_type: RelationshipType
    direction: str = "outbound"

    source_method: RelationshipSource
    evidence: list[dict[str, Any]] = []
    confidence: float = 1.0

    protocol: str | None = None
    port: int | None = None
    endpoint: str | None = None

    request_count: int | None = None
    avg_latency_ms: float | None = None
    last_seen: datetime | None = None

    discovered_at: datetime = Field(default_factory=datetime.utcnow)
    scan_id: str = ""
    human_verified: bool = False

    model_config = {"populate_by_name": True}
