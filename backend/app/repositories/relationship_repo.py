from typing import Any

from app.repositories.base import BaseRepository


class RelationshipRepository(BaseRepository):
    collection_name = "relationships"

    async def find_by_asset(self, asset_id: str) -> list[dict[str, Any]]:
        return await self.find_many({
            "$or": [
                {"source_asset_id": asset_id},
                {"target_asset_id": asset_id},
            ]
        }, limit=1000)

    async def find_by_source(self, source_asset_id: str) -> list[dict[str, Any]]:
        return await self.find_many({"source_asset_id": source_asset_id}, limit=1000)

    async def find_by_target(self, target_asset_id: str) -> list[dict[str, Any]]:
        return await self.find_many({"target_asset_id": target_asset_id}, limit=1000)

    async def upsert_relationship(
        self,
        source_id: str,
        target_id: str,
        rel_type: str,
        rel_data: dict[str, Any],
    ) -> str:
        return await self.upsert(
            {
                "source_asset_id": source_id,
                "target_asset_id": target_id,
                "relationship_type": rel_type,
            },
            rel_data,
        )

    async def get_topology(
        self,
        asset_types: list[str] | None = None,
        relationship_types: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        query: dict[str, Any] = {}
        if relationship_types:
            query["relationship_type"] = {"$in": relationship_types}
        return await self.find_many(query, limit=10000)
