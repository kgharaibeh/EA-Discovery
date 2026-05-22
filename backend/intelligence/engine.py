import json
from datetime import datetime

from intelligence.providers.base import AbstractLLMProvider
from intelligence.prompts.service_context import SERVICE_CONTEXT_SYSTEM, build_service_context_prompt
from intelligence.prompts.relationship_context import RELATIONSHIP_CONTEXT_SYSTEM, build_relationship_context_prompt
from intelligence.prompts.data_classification import DATA_CLASSIFICATION_SYSTEM, build_data_classification_prompt
from app.repositories.base import BaseRepository


class SuggestionRepository(BaseRepository):
    collection_name = "intelligence_suggestions"


class IntelligenceEngine:
    def __init__(self, provider: AbstractLLMProvider):
        self.provider = provider
        self.suggestion_repo = SuggestionRepository()

    async def analyze_asset(self, asset: dict) -> list[dict]:
        prompt = build_service_context_prompt(asset)
        result = await self.provider.infer(
            system_prompt=SERVICE_CONTEXT_SYSTEM,
            user_prompt=prompt,
        )

        suggested_value = self._parse_json_response(result["content"])
        if not suggested_value:
            return []

        suggestion = {
            "_id": self.suggestion_repo.new_id(),
            "asset_id": asset["_id"],
            "suggestion_type": "business_context",
            "suggested_value": suggested_value,
            "reasoning": suggested_value.get("reasoning", ""),
            "confidence": self._estimate_confidence(suggested_value),
            "input_data": {"hostname": asset.get("hostname"), "asset_type": asset.get("asset_type")},
            "provider": self.provider.name,
            "model": self.provider.model_name,
            "status": "pending",
            "reviewed_by": None,
            "reviewed_at": None,
            "final_value": None,
            "created_at": datetime.utcnow(),
        }
        await self.suggestion_repo.insert(suggestion)
        return [suggestion]

    async def analyze_relationship(
        self,
        relationship: dict,
        source_asset: dict,
        target_asset: dict,
    ) -> dict | None:
        prompt = build_relationship_context_prompt(source_asset, target_asset, relationship)
        result = await self.provider.infer(
            system_prompt=RELATIONSHIP_CONTEXT_SYSTEM,
            user_prompt=prompt,
        )

        suggested_value = self._parse_json_response(result["content"])
        if not suggested_value:
            return None

        suggestion = {
            "_id": self.suggestion_repo.new_id(),
            "asset_id": relationship.get("source_asset_id", ""),
            "suggestion_type": "relationship_context",
            "suggested_value": suggested_value,
            "reasoning": suggested_value.get("reasoning", ""),
            "confidence": self._estimate_confidence(suggested_value),
            "input_data": {
                "source": source_asset.get("hostname"),
                "target": target_asset.get("hostname"),
                "type": relationship.get("relationship_type"),
            },
            "provider": self.provider.name,
            "model": self.provider.model_name,
            "status": "pending",
            "reviewed_by": None,
            "reviewed_at": None,
            "final_value": None,
            "created_at": datetime.utcnow(),
        }
        await self.suggestion_repo.insert(suggestion)
        return suggestion

    async def classify_data(self, file_path: str, sample_content: str) -> dict | None:
        prompt = build_data_classification_prompt(file_path, sample_content)
        result = await self.provider.infer(
            system_prompt=DATA_CLASSIFICATION_SYSTEM,
            user_prompt=prompt,
        )

        suggested_value = self._parse_json_response(result["content"])
        if not suggested_value:
            return None

        suggestion = {
            "_id": self.suggestion_repo.new_id(),
            "asset_id": "",
            "suggestion_type": "data_classification",
            "suggested_value": suggested_value,
            "reasoning": suggested_value.get("reasoning", ""),
            "confidence": suggested_value.get("confidence", 0.5),
            "input_data": {"file_path": file_path},
            "provider": self.provider.name,
            "model": self.provider.model_name,
            "status": "pending",
            "reviewed_by": None,
            "reviewed_at": None,
            "final_value": None,
            "created_at": datetime.utcnow(),
        }
        await self.suggestion_repo.insert(suggestion)
        return suggestion

    @staticmethod
    def _parse_json_response(content: str) -> dict | None:
        try:
            start = content.find("{")
            end = content.rfind("}") + 1
            if start == -1 or end == 0:
                return None
            return json.loads(content[start:end])
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _estimate_confidence(suggested: dict) -> float:
        filled_fields = sum(1 for v in suggested.values() if v and v != "unknown")
        total_fields = len(suggested)
        return min(0.95, filled_fields / max(total_fields, 1))
