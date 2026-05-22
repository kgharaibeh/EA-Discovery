from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from app.config import settings

_client: AsyncIOMotorClient | None = None
_database: AsyncIOMotorDatabase | None = None


async def connect_db() -> None:
    global _client, _database
    _client = AsyncIOMotorClient(settings.mongodb_uri)
    _database = _client[settings.mongodb_database]
    await _create_indexes()


async def close_db() -> None:
    global _client, _database
    if _client:
        _client.close()
    _client = None
    _database = None


def get_database() -> AsyncIOMotorDatabase:
    if _database is None:
        raise RuntimeError("Database not initialized. Call connect_db() first.")
    return _database


async def _create_indexes() -> None:
    db = get_database()

    await db.assets.create_index("hostname", unique=True)
    await db.assets.create_index("ip_addresses")
    await db.assets.create_index("asset_type")
    await db.assets.create_index("last_scanned")
    await db.assets.create_index("tags")
    await db.assets.create_index(
        [("hostname", "text"), ("tags", "text")],
        name="assets_text_search",
    )

    await db.relationships.create_index(
        [("source_asset_id", 1), ("target_asset_id", 1), ("relationship_type", 1)],
        unique=True,
        name="rel_unique_triple",
    )
    await db.relationships.create_index("source_asset_id")
    await db.relationships.create_index("target_asset_id")
    await db.relationships.create_index("relationship_type")
    await db.relationships.create_index("source_method")

    await db.scans.create_index("status")
    await db.scans.create_index("created_at")

    await db.intelligence_suggestions.create_index("asset_id")
    await db.intelligence_suggestions.create_index("status")

    await db.drift_events.create_index("asset_id")
    await db.drift_events.create_index("scan_id")
    await db.drift_events.create_index("severity")
