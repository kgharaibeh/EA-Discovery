from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_asset_repo, get_relationship_repo
from app.repositories.asset_repo import AssetRepository
from app.repositories.relationship_repo import RelationshipRepository
from app.schemas.asset import AssetResponse, AssetUpdate, AssetListResponse
from app.schemas.relationship import RelationshipResponse
from app.services.asset_service import AssetService

router = APIRouter()


def _doc_to_response(doc: dict) -> AssetResponse:
    doc["id"] = doc.pop("_id")
    return AssetResponse(**doc)


def _rel_doc_to_response(doc: dict) -> RelationshipResponse:
    doc["id"] = doc.pop("_id")
    return RelationshipResponse(**doc)


@router.get("/search", response_model=AssetListResponse)
async def search_assets(
    q: str = "",
    page: int = 1,
    page_size: int = 50,
    asset_repo: AssetRepository = Depends(get_asset_repo),
):
    service = AssetService(asset_repo)
    skip = (page - 1) * page_size
    items, total = await service.list_assets(search=q, skip=skip, limit=page_size)
    return AssetListResponse(
        items=[_doc_to_response(d) for d in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/", response_model=AssetListResponse)
async def list_assets(
    asset_type: str | None = None,
    status: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 50,
    asset_repo: AssetRepository = Depends(get_asset_repo),
):
    service = AssetService(asset_repo)
    skip = (page - 1) * page_size
    items, total = await service.list_assets(
        asset_type=asset_type, status=status, search=search,
        skip=skip, limit=page_size,
    )
    return AssetListResponse(
        items=[_doc_to_response(d) for d in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{asset_id}", response_model=AssetResponse)
async def get_asset(
    asset_id: str,
    asset_repo: AssetRepository = Depends(get_asset_repo),
):
    service = AssetService(asset_repo)
    doc = await service.get_asset(asset_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Asset not found")
    return _doc_to_response(doc)


@router.patch("/{asset_id}", response_model=AssetResponse)
async def update_asset(
    asset_id: str,
    update_data: AssetUpdate,
    asset_repo: AssetRepository = Depends(get_asset_repo),
):
    service = AssetService(asset_repo)
    doc = await service.get_asset(asset_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Asset not found")
    await service.update_asset(asset_id, update_data)
    updated = await service.get_asset(asset_id)
    return _doc_to_response(updated)


@router.get("/{asset_id}/relationships", response_model=list[RelationshipResponse])
async def get_asset_relationships(
    asset_id: str,
    asset_repo: AssetRepository = Depends(get_asset_repo),
    rel_repo: RelationshipRepository = Depends(get_relationship_repo),
):
    asset = await asset_repo.find_by_id(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    docs = await rel_repo.find_by_asset(asset_id)
    return [_rel_doc_to_response(d) for d in docs]
