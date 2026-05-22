from datetime import datetime

from pydantic import BaseModel

from app.models.credential import CredentialType


class CredentialCreate(BaseModel):
    name: str
    credential_type: CredentialType
    backend: str = "encrypted_file"
    username: str | None = None
    password: str | None = None
    private_key: str | None = None
    applicable_hosts: list[str] = []


class CredentialResponse(BaseModel):
    id: str
    name: str
    credential_type: CredentialType
    backend: str
    username: str | None
    applicable_hosts: list[str]
    created_at: datetime


class CredentialTestResult(BaseModel):
    host: str
    success: bool
    message: str
