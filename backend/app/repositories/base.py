from typing import Any
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.database import get_database


class BaseRepository:
    collection_name: str = ""

    @property
    def db(self) -> AsyncIOMotorDatabase:
        return get_database()

    @property
    def collection(self):
        return self.db[self.collection_name]

    @staticmethod
    def new_id() -> str:
        return str(uuid4())

    async def find_by_id(self, doc_id: str) -> dict[str, Any] | None:
        return await self.collection.find_one({"_id": doc_id})

    async def find_many(
        self,
        query: dict[str, Any] | None = None,
        skip: int = 0,
        limit: int = 50,
        sort: list[tuple[str, int]] | None = None,
    ) -> list[dict[str, Any]]:
        cursor = self.collection.find(query or {})
        if sort:
            cursor = cursor.sort(sort)
        cursor = cursor.skip(skip).limit(limit)
        return await cursor.to_list(length=limit)

    async def count(self, query: dict[str, Any] | None = None) -> int:
        return await self.collection.count_documents(query or {})

    async def insert(self, document: dict[str, Any]) -> str:
        if "_id" not in document:
            document["_id"] = self.new_id()
        await self.collection.insert_one(document)
        return document["_id"]

    async def update(self, doc_id: str, update_data: dict[str, Any]) -> bool:
        result = await self.collection.update_one(
            {"_id": doc_id}, {"$set": update_data}
        )
        return result.modified_count > 0

    async def upsert(self, query: dict[str, Any], document: dict[str, Any]) -> str:
        if "_id" not in document:
            document["_id"] = self.new_id()
        result = await self.collection.update_one(
            query, {"$set": document}, upsert=True
        )
        if result.upserted_id:
            return str(result.upserted_id)
        existing = await self.collection.find_one(query)
        return str(existing["_id"]) if existing else document["_id"]

    async def delete(self, doc_id: str) -> bool:
        result = await self.collection.delete_one({"_id": doc_id})
        return result.deleted_count > 0
