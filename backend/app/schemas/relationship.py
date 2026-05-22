from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.models.relationship import RelationshipType, RelationshipSource


class RelationshipCreate(BaseModel):
    source_asset_id: str
    target_asset_id: str
    relationship_type: RelationshipType
    direction: str = "outbound"
    protocol: str | None = None
    port: int | None = None
    endpoint: str | None = None
    evidence: list[dict[str, Any]] = []


class RelationshipResponse(BaseModel):
    id: str
    source_asset_id: str
    target_asset_id: str
    relationship_type: RelationshipType
    direction: str
    source_method: RelationshipSource
    evidence: list[dict[str, Any]]
    confidence: float
    protocol: str | None
    port: int | None
    endpoint: str | None
    request_count: int | None
    avg_latency_ms: float | None
    last_seen: datetime | None
    discovered_at: datetime
    scan_id: str
    human_verified: bool


class RelationshipUpdate(BaseModel):
    relationship_type: RelationshipType | None = None
    human_verified: bool | None = None
    evidence: list[dict[str, Any]] | None = None


class TopologyNode(BaseModel):
    id: str
    hostname: str
    asset_type: str
    os_family: str
    status: str
    ip_addresses: list[str]
    business_context: dict[str, Any] | None = None


class TopologyEdge(BaseModel):
    id: str
    source: str
    target: str
    relationship_type: str
    source_method: str
    protocol: str | None
    port: int | None
    confidence: float


class TopologyResponse(BaseModel):
    nodes: list[TopologyNode]
    edges: list[TopologyEdge]
