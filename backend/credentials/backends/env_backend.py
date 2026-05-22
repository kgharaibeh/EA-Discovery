import os

from credentials.backends.base import AbstractCredentialBackend


class EnvBackend(AbstractCredentialBackend):
    async def get_credential(self, reference: str) -> dict:
        username = os.environ.get(f"CRED_{reference.upper()}_USER", "")
        password = os.environ.get(f"CRED_{reference.upper()}_PASS", "")
        private_key = os.environ.get(f"CRED_{reference.upper()}_KEY", "")
        result = {"username": username}
        if private_key:
            result["private_key"] = private_key
        else:
            result["password"] = password
        return result

    async def store_credential(self, reference: str, data: dict) -> None:
        pass

    async def delete_credential(self, reference: str) -> None:
        pass

    async def list_credentials(self) -> list[str]:
        prefix = "CRED_"
        suffix = "_USER"
        refs = []
        for key in os.environ:
            if key.startswith(prefix) and key.endswith(suffix):
                ref = key[len(prefix):-len(suffix)].lower()
                refs.append(ref)
        return refs
