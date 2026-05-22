from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class CredentialType(str, Enum):
    SSH_PASSWORD = "ssh_password"
    SSH_KEY = "ssh_key"
    WINRM = "winrm"
    WMI = "wmi"
    DATABASE = "database"
    LDAP = "ldap"


class Credential(BaseModel):
    id: str = Field(alias="_id")
    name: str
    credential_type: CredentialType
    backend: str = "encrypted_file"
    backend_reference: str = ""
    username: str | None = None
    applicable_hosts: list[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}
