import hvac

from app.config import settings
from credentials.backends.base import AbstractCredentialBackend


class VaultBackend(AbstractCredentialBackend):
    def __init__(self):
        self._client = hvac.Client(url=settings.vault_url, token=settings.vault_token)
        self._mount_point = "secret"
        self._base_path = "ea-discovery/credentials"

    async def get_credential(self, reference: str) -> dict:
        path = f"{self._base_path}/{reference}"
        response = self._client.secrets.kv.v2.read_secret_version(
            path=path, mount_point=self._mount_point
        )
        return response["data"]["data"]

    async def store_credential(self, reference: str, data: dict) -> None:
        path = f"{self._base_path}/{reference}"
        self._client.secrets.kv.v2.create_or_update_secret(
            path=path, secret=data, mount_point=self._mount_point
        )

    async def delete_credential(self, reference: str) -> None:
        path = f"{self._base_path}/{reference}"
        self._client.secrets.kv.v2.delete_metadata_and_all_versions(
            path=path, mount_point=self._mount_point
        )

    async def list_credentials(self) -> list[str]:
        try:
            response = self._client.secrets.kv.v2.list_secrets(
                path=self._base_path, mount_point=self._mount_point
            )
            return response["data"]["keys"]
        except Exception:
            return []
