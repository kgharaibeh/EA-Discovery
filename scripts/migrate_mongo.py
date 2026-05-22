"""Create MongoDB indexes for EA Discovery."""
import asyncio

from motor.motor_asyncio import AsyncIOMotorClient


async def migrate():
    client = AsyncIOMotorClient("mongodb://localhost:27017/ea_discovery")
    db = client["ea_discovery"]

    print("Creating indexes...")

    await db.assets.create_index("hostname", unique=True)
    await db.assets.create_index("ip_addresses")
    await db.assets.create_index("asset_type")
    await db.assets.create_index("last_scanned")
    await db.assets.create_index("tags")
    await db.assets.create_index(
        [("hostname", "text"), ("tags", "text")],
        name="assets_text_search",
    )
    print("  assets: 6 indexes")

    await db.relationships.create_index(
        [("source_asset_id", 1), ("target_asset_id", 1), ("relationship_type", 1)],
        unique=True,
        name="rel_unique_triple",
    )
    await db.relationships.create_index("source_asset_id")
    await db.relationships.create_index("target_asset_id")
    await db.relationships.create_index("relationship_type")
    await db.relationships.create_index("source_method")
    print("  relationships: 5 indexes")

    await db.scans.create_index("status")
    await db.scans.create_index("created_at")
    print("  scans: 2 indexes")

    await db.intelligence_suggestions.create_index("asset_id")
    await db.intelligence_suggestions.create_index("status")
    print("  intelligence_suggestions: 2 indexes")

    await db.drift_events.create_index("asset_id")
    await db.drift_events.create_index("scan_id")
    await db.drift_events.create_index("severity")
    print("  drift_events: 3 indexes")

    print("\nDone. All indexes created.")
    client.close()


if __name__ == "__main__":
    asyncio.run(migrate())
