from typing import Any

from app.repositories.base import BaseRepository


class ScanRepository(BaseRepository):
    collection_name = "scans"

    async def find_latest_for_target(self, host: str) -> dict[str, Any] | None:
        results = await self.find_many(
            {"targets.host": host, "status": "completed"},
            sort=[("completed_at", -1)],
            limit=1,
        )
        return results[0] if results else None

    async def find_by_status(self, status: str, skip: int = 0, limit: int = 50) -> list[dict[str, Any]]:
        return await self.find_many({"status": status}, skip=skip, limit=limit)
