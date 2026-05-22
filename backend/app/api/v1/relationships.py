from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.dependencies import get_asset_repo, get_relationship_repo
from app.repositories.asset_repo import AssetRepository
from app.repositories.relationship_repo import RelationshipRepository
from app.schemas.relationship import (
    RelationshipCreate,
    RelationshipResponse,
    RelationshipUpdate,
    TopologyResponse,
)
from app.services.relationship_service import RelationshipService

router = APIRouter()


def _doc_to_response(doc: dict) -> RelationshipResponse:
    doc["id"] = doc.pop("_id")
    return RelationshipResponse(**doc)


@router.get("/topology", response_model=TopologyResponse)
async def get_topology(
    asset_types: list[str] | None = Query(default=None),
    relationship_types: list[str] | None = Query(default=None),
    asset_repo: AssetRepository = Depends(get_asset_repo),
    rel_repo: RelationshipRepository = Depends(get_relationship_repo),
):
    service = RelationshipService(rel_repo, asset_repo)
    return await service.get_topology(
        asset_types=asset_types, relationship_types=relationship_types
    )


@router.get("/", response_model=list[RelationshipResponse])
async def list_relationships(
    relationship_type: str | None = None,
    source_method: str | None = None,
    page: int = 1,
    page_size: int = 50,
    asset_repo: AssetRepository = Depends(get_asset_repo),
    rel_repo: RelationshipRepository = Depends(get_relationship_repo),
):
    service = RelationshipService(rel_repo, asset_repo)
    skip = (page - 1) * page_size
    items, _ = await service.list_relationships(
        rel_type=relationship_type,
        source_method=source_method,
        skip=skip,
        limit=page_size,
    )
    return [_doc_to_response(d) for d in items]


@router.post("/", response_model=RelationshipResponse, status_code=status.HTTP_201_CREATED)
async def create_relationship(
    data: RelationshipCreate,
    asset_repo: AssetRepository = Depends(get_asset_repo),
    rel_repo: RelationshipRepository = Depends(get_relationship_repo),
):
    source = await asset_repo.find_by_id(data.source_asset_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source asset not found")
    target = await asset_repo.find_by_id(data.target_asset_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target asset not found")

    service = RelationshipService(rel_repo, asset_repo)
    doc = await service.create_relationship(data)
    return _doc_to_response(doc)


@router.patch("/{rel_id}", response_model=RelationshipResponse)
async def update_relationship(
    rel_id: str,
    update_data: RelationshipUpdate,
    asset_repo: AssetRepository = Depends(get_asset_repo),
    rel_repo: RelationshipRepository = Depends(get_relationship_repo),
):
    service = RelationshipService(rel_repo, asset_repo)
    existing = await rel_repo.find_by_id(rel_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Relationship not found")
    updates = update_data.model_dump(exclude_none=True)
    if updates:
        await service.update_relationship(rel_id, updates)
    updated = await rel_repo.find_by_id(rel_id)
    return _doc_to_response(updated)


@router.delete("/{rel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_relationship(
    rel_id: str,
    asset_repo: AssetRepository = Depends(get_asset_repo),
    rel_repo: RelationshipRepository = Depends(get_relationship_repo),
):
    service = RelationshipService(rel_repo, asset_repo)
    existing = await rel_repo.find_by_id(rel_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Relationship not found")
    await service.delete_relationship(rel_id)
