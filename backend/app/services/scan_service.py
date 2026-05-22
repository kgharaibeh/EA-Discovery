from datetime import datetime

from app.repositories.scan_repo import ScanRepository
from app.schemas.scan import ScanCreate


class ScanService:
    def __init__(self, scan_repo: ScanRepository):
        self.scan_repo = scan_repo

    async def create_scan(self, scan_data: ScanCreate) -> dict:
        scan_id = self.scan_repo.new_id()
        scan_doc = {
            "_id": scan_id,
            "scan_type": scan_data.scan_type.value,
            "status": "pending",
            "targets": scan_data.targets,
            "scope": scan_data.scope,
            "total_targets": len(scan_data.targets),
            "completed_targets": 0,
            "failed_targets": [],
            "assets_discovered": 0,
            "relationships_discovered": 0,
            "new_assets": 0,
            "updated_assets": 0,
            "created_at": datetime.utcnow(),
            "started_at": None,
            "completed_at": None,
            "celery_task_id": None,
            "initiated_by": "manual",
            "schedule_id": None,
        }
        await self.scan_repo.insert(scan_doc)
        return scan_doc

    async def get_scan(self, scan_id: str) -> dict | None:
        return await self.scan_repo.find_by_id(scan_id)

    async def list_scans(self, status: str | None = None, skip: int = 0, limit: int = 50) -> tuple[list[dict], int]:
        query = {}
        if status:
            query["status"] = status
        items = await self.scan_repo.find_many(query, skip=skip, limit=limit, sort=[("created_at", -1)])
        total = await self.scan_repo.count(query)
        return items, total

    async def update_scan_status(self, scan_id: str, status: str, **kwargs) -> bool:
        update_data = {"status": status, **kwargs}
        if status == "running":
            update_data["started_at"] = datetime.utcnow()
        elif status in ("completed", "failed", "cancelled"):
            update_data["completed_at"] = datetime.utcnow()
        return await self.scan_repo.update(scan_id, update_data)

    async def update_scan_progress(self, scan_id: str, completed: int, failed: list[dict] | None = None) -> bool:
        update_data: dict = {"completed_targets": completed}
        if failed:
            update_data["failed_targets"] = failed
        return await self.scan_repo.update(scan_id, update_data)
