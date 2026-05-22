import asyncio

from tasks.celery_app import celery_app


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="tasks.analyze_asset")
def analyze_asset(asset_id: str):
    _run_async(_analyze_asset_async(asset_id))


async def _analyze_asset_async(asset_id: str):
    from app.core.database import connect_db, close_db
    from app.repositories.asset_repo import AssetRepository
    from app.config import settings
    from intelligence.engine import IntelligenceEngine
    from intelligence.provider_registry import llm_registry

    await connect_db()
    try:
        asset_repo = AssetRepository()
        asset = await asset_repo.find_by_id(asset_id)
        if not asset:
            return

        try:
            provider_cls = llm_registry.get(settings.llm_provider)
            provider = provider_cls()
        except ValueError:
            return

        engine = IntelligenceEngine(provider)
        await engine.analyze_asset(asset)
    finally:
        from app.core.database import close_db
        await close_db()
