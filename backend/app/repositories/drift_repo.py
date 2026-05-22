from typing import Any

from app.repositories.base import BaseRepository


class DriftRepository(BaseRepository):
    collection_name = "drift_events"

    async def find_by_asset(self, asset_id: str, skip: int = 0, limit: int = 50) -> list[dict[str, Any]]:
        return await self.find_many(
            {"asset_id": asset_id},
            skip=skip,
            limit=limit,
            sort=[("detected_at", -1)],
        )

    async def find_by_severity(self, severity: str, skip: int = 0, limit: int = 50) -> list[dict[str, Any]]:
        return await self.find_many({"severity": severity}, skip=skip, limit=limit)

    async def find_unacknowledged(self, skip: int = 0, limit: int = 50) -> list[dict[str, Any]]:
        return await self.find_many({"acknowledged": False}, skip=skip, limit=limit)
