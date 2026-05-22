import asyncio

from tasks.celery_app import celery_app


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="tasks.generate_export")
def generate_export(format: str = "drawio", asset_types: list | None = None, relationship_types: list | None = None):
    return _run_async(_generate_export_async(format, asset_types, relationship_types))


async def _generate_export_async(format: str, asset_types: list | None, relationship_types: list | None) -> str:
    from app.core.database import connect_db, close_db
    from app.repositories.asset_repo import AssetRepository
    from app.repositories.relationship_repo import RelationshipRepository
    from app.services.relationship_service import RelationshipService
    from app.services.export_service import ExportService

    await connect_db()
    try:
        rel_repo = RelationshipRepository()
        asset_repo = AssetRepository()
        rel_service = RelationshipService(rel_repo, asset_repo)
        export_service = ExportService(rel_service)

        if format == "csv":
            return await export_service.export_csv(asset_types=asset_types)
        return await export_service.export_drawio(
            asset_types=asset_types,
            relationship_types=relationship_types,
        )
    finally:
        await close_db()
