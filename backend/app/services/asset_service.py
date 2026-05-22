from app.repositories.asset_repo import AssetRepository
from app.schemas.asset import AssetUpdate


class AssetService:
    def __init__(self, asset_repo: AssetRepository):
        self.asset_repo = asset_repo

    async def get_asset(self, asset_id: str) -> dict | None:
        return await self.asset_repo.find_by_id(asset_id)

    async def list_assets(
        self,
        asset_type: str | None = None,
        status: str | None = None,
        search: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[dict], int]:
        query: dict = {}
        if asset_type:
            query["asset_type"] = asset_type
        if status:
            query["status"] = status

        if search:
            items = await self.asset_repo.search(search, skip=skip, limit=limit)
            total = len(items)
        else:
            items = await self.asset_repo.find_many(query, skip=skip, limit=limit, sort=[("last_scanned", -1)])
            total = await self.asset_repo.count(query)

        return items, total

    async def update_asset(self, asset_id: str, update_data: AssetUpdate) -> bool:
        updates = update_data.model_dump(exclude_none=True)
        if not updates:
            return False
        return await self.asset_repo.update(asset_id, updates)

    async def get_asset_by_hostname(self, hostname: str) -> dict | None:
        return await self.asset_repo.find_by_hostname(hostname)
