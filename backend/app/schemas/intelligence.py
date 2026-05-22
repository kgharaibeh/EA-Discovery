from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.models.intelligence import SuggestionStatus


class SuggestionResponse(BaseModel):
    id: str
    asset_id: str
    suggestion_type: str
    suggested_value: dict[str, Any]
    reasoning: str
    confidence: float
    provider: str
    model: str
    status: SuggestionStatus
    reviewed_by: str | None
    reviewed_at: datetime | None
    final_value: dict[str, Any] | None
    created_at: datetime


class SuggestionReview(BaseModel):
    action: SuggestionStatus
    final_value: dict[str, Any] | None = None
    reviewed_by: str = "admin"
