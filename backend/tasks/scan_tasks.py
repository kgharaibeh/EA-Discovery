import asyncio
from datetime import datetime

from tasks.celery_app import celery_app


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(bind=True, name="tasks.execute_scan")
def execute_scan(self, scan_id: str):
    _run_async(_execute_scan_async(self, scan_id))


async def _execute_scan_async(task, scan_id: str):
    from app.core.database import connect_db, close_db, get_database
    from app.repositories.scan_repo import ScanRepository
    from app.repositories.asset_repo import AssetRepository
    from app.repositories.relationship_repo import RelationshipRepository
    from scanner.engine import ScanEngine
    from credentials.manager import CredentialManager

    await connect_db()
    try:
        scan_repo = ScanRepository()
        asset_repo = AssetRepository()
        rel_repo = RelationshipRepository()

        scan = await scan_repo.find_by_id(scan_id)
        if not scan:
            return

        await scan_repo.update(scan_id, {
            "status": "running",
            "started_at": datetime.utcnow(),
            "celery_task_id": task.request.id,
        })

        engine = ScanEngine(
            credential_manager=CredentialManager(),
            asset_repo=asset_repo,
            relationship_repo=rel_repo,
        )

        result = await engine.execute_scan(scan)

        await scan_repo.update(scan_id, {
            "status": "completed",
            "completed_at": datetime.utcnow(),
            "assets_discovered": result.get("assets_discovered", 0),
            "relationships_discovered": result.get("relationships_discovered", 0),
            "new_assets": result.get("new_assets", 0),
            "updated_assets": result.get("updated_assets", 0),
            "completed_targets": result.get("completed_targets", 0),
            "failed_targets": result.get("failed_targets", []),
        })

    except Exception as e:
        await scan_repo.update(scan_id, {
            "status": "failed",
            "completed_at": datetime.utcnow(),
            "failed_targets": [{"error": str(e)}],
        })
        raise
    finally:
        await close_db()
