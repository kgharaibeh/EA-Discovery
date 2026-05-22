from typing import Any

from fastapi import APIRouter, Depends

from app.dependencies import get_asset_repo, get_relationship_repo, get_scan_repo, get_drift_repo
from app.repositories.asset_repo import AssetRepository
from app.repositories.relationship_repo import RelationshipRepository
from app.repositories.scan_repo import ScanRepository
from app.repositories.drift_repo import DriftRepository

router = APIRouter()


@router.get("/stats")
async def get_stats(
    asset_repo: AssetRepository = Depends(get_asset_repo),
    rel_repo: RelationshipRepository = Depends(get_relationship_repo),
    scan_repo: ScanRepository = Depends(get_scan_repo),
    drift_repo: DriftRepository = Depends(get_drift_repo),
) -> dict[str, Any]:
    # Assets by type
    assets_by_type = await asset_repo.collection.aggregate([
        {"$group": {"_id": "$asset_type", "count": {"$sum": 1}}}
    ]).to_list(length=100)

    # Relationships by type
    rels_by_type = await rel_repo.collection.aggregate([
        {"$group": {"_id": "$relationship_type", "count": {"$sum": 1}}}
    ]).to_list(length=100)

    total_assets = await asset_repo.count()
    total_relationships = await rel_repo.count()
    total_scans = await scan_repo.count()
    unacknowledged_drift = await drift_repo.count({"acknowledged": False})

    return {
        "total_assets": total_assets,
        "total_relationships": total_relationships,
        "total_scans": total_scans,
        "unacknowledged_drift_events": unacknowledged_drift,
        "assets_by_type": {
            item["_id"]: item["count"] for item in assets_by_type if item["_id"]
        },
        "relationships_by_type": {
            item["_id"]: item["count"] for item in rels_by_type if item["_id"]
        },
    }


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    scan_repo: ScanRepository = Depends(get_scan_repo),
    drift_repo: DriftRepository = Depends(get_drift_repo),
) -> dict[str, Any]:
    recent_scans = await scan_repo.find_many(
        sort=[("created_at", -1)], limit=limit
    )
    for s in recent_scans:
        s["id"] = s.pop("_id")

    recent_drift = await drift_repo.find_many(
        sort=[("detected_at", -1)], limit=limit
    )
    for d in recent_drift:
        d["id"] = d.pop("_id")

    return {
        "recent_scans": recent_scans,
        "recent_drift_events": recent_drift,
    }
