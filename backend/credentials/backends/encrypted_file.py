import json
import os
from pathlib import Path

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

from app.config import settings
from credentials.backends.base import AbstractCredentialBackend


class EncryptedFileBackend(AbstractCredentialBackend):
    def __init__(self):
        self._store_path = Path("credentials/store")
        self._store_path.mkdir(parents=True, exist_ok=True)
        self._fernet = self._create_fernet()

    def _create_fernet(self) -> Fernet:
        key_material = settings.credential_master_key.encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"ea-discovery-salt",
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(key_material))
        return Fernet(key)

    async def get_credential(self, reference: str) -> dict:
        file_path = self._store_path / f"{reference}.enc"
        if not file_path.exists():
            raise FileNotFoundError(f"Credential '{reference}' not found")
        encrypted_data = file_path.read_bytes()
        decrypted = self._fernet.decrypt(encrypted_data)
        return json.loads(decrypted)

    async def store_credential(self, reference: str, data: dict) -> None:
        file_path = self._store_path / f"{reference}.enc"
        json_data = json.dumps(data).encode()
        encrypted = self._fernet.encrypt(json_data)
        file_path.write_bytes(encrypted)

    async def delete_credential(self, reference: str) -> None:
        file_path = self._store_path / f"{reference}.enc"
        if file_path.exists():
            file_path.unlink()

    async def list_credentials(self) -> list[str]:
        return [f.stem for f in self._store_path.glob("*.enc")]
