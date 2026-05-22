from datetime import datetime

from app.repositories.base import BaseRepository


class ReviewableManager:
    def __init__(self):
        self.repo = BaseRepository()
        self.repo.collection_name = "intelligence_suggestions"

    async def accept(self, suggestion_id: str, reviewed_by: str = "admin", final_value: dict | None = None) -> bool:
        suggestion = await self.repo.find_by_id(suggestion_id)
        if not suggestion:
            return False

        update = {
            "status": "accepted",
            "reviewed_by": reviewed_by,
            "reviewed_at": datetime.utcnow(),
            "final_value": final_value or suggestion.get("suggested_value"),
        }
        return await self.repo.update(suggestion_id, update)

    async def reject(self, suggestion_id: str, reviewed_by: str = "admin") -> bool:
        return await self.repo.update(suggestion_id, {
            "status": "rejected",
            "reviewed_by": reviewed_by,
            "reviewed_at": datetime.utcnow(),
        })

    async def modify(self, suggestion_id: str, final_value: dict, reviewed_by: str = "admin") -> bool:
        return await self.repo.update(suggestion_id, {
            "status": "modified",
            "final_value": final_value,
            "reviewed_by": reviewed_by,
            "reviewed_at": datetime.utcnow(),
        })
