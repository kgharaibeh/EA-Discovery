from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_asset_repo
from app.repositories.asset_repo import AssetRepository
from app.repositories.base import BaseRepository
from app.schemas.intelligence import SuggestionResponse, SuggestionReview
from app.models.intelligence import SuggestionStatus

router = APIRouter()


class SuggestionRepository(BaseRepository):
    collection_name = "intelligence_suggestions"


def _get_suggestion_repo() -> SuggestionRepository:
    return SuggestionRepository()


def _doc_to_response(doc: dict) -> SuggestionResponse:
    doc["id"] = doc.pop("_id")
    return SuggestionResponse(**doc)


@router.get("/suggestions", response_model=list[SuggestionResponse])
async def list_suggestions(
    status_filter: str | None = None,
    page: int = 1,
    page_size: int = 50,
    repo: SuggestionRepository = Depends(_get_suggestion_repo),
):
    query: dict[str, Any] = {}
    if status_filter:
        query["status"] = status_filter
    else:
        query["status"] = SuggestionStatus.PENDING.value
    skip = (page - 1) * page_size
    items = await repo.find_many(query, skip=skip, limit=page_size)
    return [_doc_to_response(d) for d in items]


@router.get("/suggestions/{suggestion_id}", response_model=SuggestionResponse)
async def get_suggestion(
    suggestion_id: str,
    repo: SuggestionRepository = Depends(_get_suggestion_repo),
):
    doc = await repo.find_by_id(suggestion_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Suggestion not found")
    return _doc_to_response(doc)


@router.post("/suggestions/{suggestion_id}/review", response_model=SuggestionResponse)
async def review_suggestion(
    suggestion_id: str,
    review: SuggestionReview,
    repo: SuggestionRepository = Depends(_get_suggestion_repo),
    asset_repo: AssetRepository = Depends(get_asset_repo),
):
    doc = await repo.find_by_id(suggestion_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    if doc["status"] != SuggestionStatus.PENDING.value:
        raise HTTPException(status_code=400, detail="Suggestion already reviewed")

    from datetime import datetime

    update_data: dict[str, Any] = {
        "status": review.action.value,
        "reviewed_by": review.reviewed_by,
        "reviewed_at": datetime.utcnow(),
    }

    if review.action == SuggestionStatus.ACCEPTED:
        final_value = review.final_value or doc.get("suggested_value", {})
        update_data["final_value"] = final_value
        # Apply the accepted suggestion to the asset
        asset_id = doc["asset_id"]
        suggestion_type = doc.get("suggestion_type", "business_context")
        await asset_repo.update(asset_id, {suggestion_type: final_value})
    elif review.action == SuggestionStatus.MODIFIED:
        if not review.final_value:
            raise HTTPException(
                status_code=400, detail="final_value required for modified action"
            )
        update_data["final_value"] = review.final_value
        asset_id = doc["asset_id"]
        suggestion_type = doc.get("suggestion_type", "business_context")
        await asset_repo.update(asset_id, {suggestion_type: review.final_value})

    await repo.update(suggestion_id, update_data)
    updated = await repo.find_by_id(suggestion_id)
    return _doc_to_response(updated)
