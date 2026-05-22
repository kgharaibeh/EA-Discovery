from typing import Any

from app.repositories.base import BaseRepository


class AssetRepository(BaseRepository):
    collection_name = "assets"

    async def find_by_hostname(self, hostname: str) -> dict[str, Any] | None:
        return await self.collection.find_one({"hostname": hostname})

    async def find_by_ip(self, ip_address: str) -> dict[str, Any] | None:
        return await self.collection.find_one({"ip_addresses": ip_address})

    async def find_by_type(self, asset_type: str, skip: int = 0, limit: int = 50) -> list[dict[str, Any]]:
        return await self.find_many({"asset_type": asset_type}, skip=skip, limit=limit)

    async def search(self, query_text: str, skip: int = 0, limit: int = 50) -> list[dict[str, Any]]:
        return await self.find_many(
            {"$text": {"$search": query_text}},
            skip=skip,
            limit=limit,
        )

    async def upsert_by_hostname(self, hostname: str, asset_data: dict[str, Any]) -> str:
        return await self.upsert({"hostname": hostname}, asset_data)

    async def resolve_by_ip_port(self, ip: str, port: int | None = None) -> dict[str, Any] | None:
        doc = await self.find_by_ip(ip)
        if doc:
            return doc
        doc = await self.find_by_hostname(ip)
        return doc
