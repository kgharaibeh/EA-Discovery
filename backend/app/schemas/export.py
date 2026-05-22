from pydantic import BaseModel


class ExportRequest(BaseModel):
    format: str = "drawio"
    asset_types: list[str] | None = None
    relationship_types: list[str] | None = None
    tags: list[str] | None = None


class ExportResponse(BaseModel):
    id: str
    format: str
    status: str
    download_url: str | None = None
