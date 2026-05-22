from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_drift_repo
from app.repositories.drift_repo import DriftRepository
from app.services.drift_service import DriftService

router = APIRouter()


def _doc_to_response(doc: dict) -> dict:
    doc["id"] = doc.pop("_id")
    return doc


@router.get("/events")
async def list_drift_events(
    severity: str | None = None,
    asset_id: str | None = None,
    page: int = 1,
    page_size: int = 50,
    drift_repo: DriftRepository = Depends(get_drift_repo),
):
    service = DriftService(drift_repo)
    skip = (page - 1) * page_size
    items, total = await service.list_events(
        asset_id=asset_id, severity=severity, skip=skip, limit=page_size
    )
    return {
        "items": [_doc_to_response(d) for d in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.post("/events/{event_id}/acknowledge")
async def acknowledge_drift_event(
    event_id: str,
    drift_repo: DriftRepository = Depends(get_drift_repo),
):
    service = DriftService(drift_repo)
    existing = await drift_repo.find_by_id(event_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Drift event not found")
    if existing.get("acknowledged"):
        raise HTTPException(status_code=400, detail="Drift event already acknowledged")
    await service.acknowledge(event_id)
    updated = await drift_repo.find_by_id(event_id)
    return _doc_to_response(updated)
