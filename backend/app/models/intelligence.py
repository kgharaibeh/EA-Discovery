from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SuggestionStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    MODIFIED = "modified"


class IntelligenceSuggestion(BaseModel):
    id: str = Field(alias="_id")
    asset_id: str
    suggestion_type: str = "business_context"

    suggested_value: dict[str, Any] = {}
    reasoning: str = ""
    confidence: float = 0.0

    input_data: dict[str, Any] = {}
    provider: str = ""
    model: str = ""

    status: SuggestionStatus = SuggestionStatus.PENDING
    reviewed_by: str | None = None
    reviewed_at: datetime | None = None
    final_value: dict[str, Any] | None = None

    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}
