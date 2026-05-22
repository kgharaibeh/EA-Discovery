from datetime import datetime

from app.repositories.base import BaseRepository


class ScheduleRepository(BaseRepository):
    collection_name = "schedules"


class ScheduleService:
    def __init__(self):
        self.repo = ScheduleRepository()

    async def create_schedule(self, data: dict) -> dict:
        schedule_id = self.repo.new_id()
        doc = {
            "_id": schedule_id,
            "name": data["name"],
            "cron_expression": data.get("cron_expression", "0 2 * * *"),
            "scan_config": data.get("scan_config", {}),
            "enabled": data.get("enabled", True),
            "last_run": None,
            "next_run": None,
            "created_at": datetime.utcnow(),
        }
        await self.repo.insert(doc)
        return doc

    async def list_schedules(self, skip: int = 0, limit: int = 50) -> tuple[list[dict], int]:
        items = await self.repo.find_many(skip=skip, limit=limit)
        total = await self.repo.count()
        return items, total

    async def update_schedule(self, schedule_id: str, data: dict) -> bool:
        return await self.repo.update(schedule_id, data)

    async def delete_schedule(self, schedule_id: str) -> bool:
        return await self.repo.delete(schedule_id)
