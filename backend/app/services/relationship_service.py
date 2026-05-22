from datetime import datetime

from app.repositories.asset_repo import AssetRepository
from app.repositories.relationship_repo import RelationshipRepository
from app.schemas.relationship import RelationshipCreate, TopologyNode, TopologyEdge, TopologyResponse


class RelationshipService:
    def __init__(self, rel_repo: RelationshipRepository, asset_repo: AssetRepository):
        self.rel_repo = rel_repo
        self.asset_repo = asset_repo

    async def create_relationship(self, data: RelationshipCreate) -> dict:
        rel_id = self.rel_repo.new_id()
        rel_doc = {
            "_id": rel_id,
            "source_asset_id": data.source_asset_id,
            "target_asset_id": data.target_asset_id,
            "relationship_type": data.relationship_type.value,
            "direction": data.direction,
            "source_method": "manual",
            "evidence": data.evidence,
            "confidence": 1.0,
            "protocol": data.protocol,
            "port": data.port,
            "endpoint": data.endpoint,
            "request_count": None,
            "avg_latency_ms": None,
            "last_seen": None,
            "discovered_at": datetime.utcnow(),
            "scan_id": "",
            "human_verified": True,
        }
        await self.rel_repo.insert(rel_doc)
        return rel_doc

    async def get_relationships_for_asset(self, asset_id: str) -> list[dict]:
        return await self.rel_repo.find_by_asset(asset_id)

    async def list_relationships(
        self,
        rel_type: str | None = None,
        source_method: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        query: dict = {}
        if rel_type:
            query["relationship_type"] = rel_type
        if source_method:
            query["source_method"] = source_method
        items = await self.rel_repo.find_many(query, skip=skip, limit=limit)
        total = await self.rel_repo.count(query)
        return items, total

    async def get_topology(
        self,
        asset_types: list[str] | None = None,
        relationship_types: list[str] | None = None,
    ) -> TopologyResponse:
        rels = await self.rel_repo.get_topology(
            asset_types=asset_types,
            relationship_types=relationship_types,
        )

        asset_ids: set[str] = set()
        for r in rels:
            asset_ids.add(r["source_asset_id"])
            asset_ids.add(r["target_asset_id"])

        nodes: list[TopologyNode] = []
        for aid in asset_ids:
            asset = await self.asset_repo.find_by_id(aid)
            if asset:
                if asset_types and asset["asset_type"] not in asset_types:
                    continue
                nodes.append(TopologyNode(
                    id=asset["_id"],
                    hostname=asset["hostname"],
                    asset_type=asset["asset_type"],
                    os_family=asset.get("os_family", "unknown"),
                    status=asset.get("status", "unknown"),
                    ip_addresses=asset.get("ip_addresses", []),
                    business_context=asset.get("business_context"),
                ))

        node_ids = {n.id for n in nodes}
        edges: list[TopologyEdge] = []
        for r in rels:
            if r["source_asset_id"] in node_ids and r["target_asset_id"] in node_ids:
                edges.append(TopologyEdge(
                    id=r["_id"],
                    source=r["source_asset_id"],
                    target=r["target_asset_id"],
                    relationship_type=r["relationship_type"],
                    source_method=r.get("source_method", "unknown"),
                    protocol=r.get("protocol"),
                    port=r.get("port"),
                    confidence=r.get("confidence", 1.0),
                ))

        return TopologyResponse(nodes=nodes, edges=edges)

    async def update_relationship(self, rel_id: str, update_data: dict) -> bool:
        return await self.rel_repo.update(rel_id, update_data)

    async def delete_relationship(self, rel_id: str) -> bool:
        return await self.rel_repo.delete(rel_id)
