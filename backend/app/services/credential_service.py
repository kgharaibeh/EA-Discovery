from datetime import datetime

from app.repositories.base import BaseRepository


class CredentialRepository(BaseRepository):
    collection_name = "credentials"


class CredentialService:
    def __init__(self):
        self.repo = CredentialRepository()

    async def create_credential(self, data: dict) -> dict:
        cred_id = self.repo.new_id()
        cred_doc = {
            "_id": cred_id,
            "name": data["name"],
            "credential_type": data["credential_type"],
            "backend": data.get("backend", "encrypted_file"),
            "backend_reference": cred_id,
            "username": data.get("username"),
            "applicable_hosts": data.get("applicable_hosts", []),
            "created_at": datetime.utcnow(),
        }
        await self.repo.insert(cred_doc)
        return cred_doc

    async def list_credentials(self, skip: int = 0, limit: int = 50) -> tuple[list[dict], int]:
        items = await self.repo.find_many(skip=skip, limit=limit)
        total = await self.repo.count()
        return items, total

    async def get_credential(self, cred_id: str) -> dict | None:
        return await self.repo.find_by_id(cred_id)

    async def delete_credential(self, cred_id: str) -> bool:
        return await self.repo.delete(cred_id)

    async def find_for_host(self, host: str) -> dict | None:
        creds = await self.repo.find_many(limit=100)
        for cred in creds:
            patterns = cred.get("applicable_hosts", [])
            if not patterns:
                continue
            for pattern in patterns:
                if pattern == "*" or pattern == host:
                    return cred
                if pattern.startswith("*") and host.endswith(pattern[1:]):
                    return cred
        return None
