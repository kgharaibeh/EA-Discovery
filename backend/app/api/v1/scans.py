from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_scan_repo
from app.repositories.scan_repo import ScanRepository
from app.schemas.scan import ScanCreate, ScanResponse, ScanListResponse
from app.services.scan_service import ScanService

router = APIRouter()


def _doc_to_response(doc: dict) -> ScanResponse:
    doc["id"] = doc.pop("_id")
    return ScanResponse(**doc)


@router.post("/", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    scan_data: ScanCreate,
    scan_repo: ScanRepository = Depends(get_scan_repo),
):
    service = ScanService(scan_repo)
    doc = await service.create_scan(scan_data)
    return _doc_to_response(doc)


@router.get("/", response_model=ScanListResponse)
async def list_scans(
    status_filter: str | None = None,
    page: int = 1,
    page_size: int = 50,
    scan_repo: ScanRepository = Depends(get_scan_repo),
):
    service = ScanService(scan_repo)
    skip = (page - 1) * page_size
    items, total = await service.list_scans(
        status=status_filter, skip=skip, limit=page_size
    )
    return ScanListResponse(
        items=[_doc_to_response(d) for d in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(
    scan_id: str,
    scan_repo: ScanRepository = Depends(get_scan_repo),
):
    service = ScanService(scan_repo)
    doc = await service.get_scan(scan_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Scan not found")
    return _doc_to_response(doc)


@router.post("/{scan_id}/cancel", response_model=ScanResponse)
async def cancel_scan(
    scan_id: str,
    scan_repo: ScanRepository = Depends(get_scan_repo),
):
    service = ScanService(scan_repo)
    doc = await service.get_scan(scan_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Scan not found")
    if doc["status"] not in ("pending", "running"):
        raise HTTPException(
            status_code=400, detail="Only pending or running scans can be cancelled"
        )
    await service.update_scan_status(scan_id, "cancelled")
    updated = await service.get_scan(scan_id)
    return _doc_to_response(updated)
