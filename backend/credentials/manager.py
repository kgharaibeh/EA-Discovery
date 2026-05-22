from app.config import settings
from credentials.backends.base import AbstractCredentialBackend
from credentials.backends.encrypted_file import EncryptedFileBackend
from credentials.backends.vault_backend import VaultBackend
from credentials.backends.env_backend import EnvBackend


class CredentialManager:
    def __init__(self):
        self._backend = self._create_backend()

    def _create_backend(self) -> AbstractCredentialBackend:
        backends = {
            "encrypted_file": EncryptedFileBackend,
            "vault": VaultBackend,
            "env": EnvBackend,
        }
        backend_cls = backends.get(settings.credential_backend)
        if not backend_cls:
            raise ValueError(f"Unknown credential backend: {settings.credential_backend}")
        return backend_cls()

    async def get_credential(self, reference: str) -> dict:
        return await self._backend.get_credential(reference)

    async def store_credential(self, reference: str, data: dict) -> None:
        await self._backend.store_credential(reference, data)

    async def delete_credential(self, reference: str) -> None:
        await self._backend.delete_credential(reference)

    async def list_credentials(self) -> list[str]:
        return await self._backend.list_credentials()
