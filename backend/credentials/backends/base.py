from abc import ABC, abstractmethod


class AbstractCredentialBackend(ABC):
    @abstractmethod
    async def get_credential(self, reference: str) -> dict:
        """Returns {"username": str, "password": str} or {"username": str, "private_key": str}"""
        ...

    @abstractmethod
    async def store_credential(self, reference: str, data: dict) -> None: ...

    @abstractmethod
    async def delete_credential(self, reference: str) -> None: ...

    @abstractmethod
    async def list_credentials(self) -> list[str]: ...
