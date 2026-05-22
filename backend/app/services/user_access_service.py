from app.repositories.base import BaseRepository


class UserAccessRepository(BaseRepository):
    collection_name = "user_access"


class UserAccessService:
    def __init__(self):
        self.repo = UserAccessRepository()

    async def list_user_access(self, asset_id: str | None = None, skip: int = 0, limit: int = 50) -> tuple[list[dict], int]:
        query: dict = {}
        if asset_id:
            query["asset_id"] = asset_id
        items = await self.repo.find_many(query, skip=skip, limit=limit)
        total = await self.repo.count(query)
        return items, total
