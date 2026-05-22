from fastapi import APIRouter, HTTPException, status

from app.schemas.credential import CredentialCreate, CredentialResponse
from app.services.credential_service import CredentialService

router = APIRouter()


def _doc_to_response(doc: dict) -> CredentialResponse:
    doc["id"] = doc.pop("_id")
    return CredentialResponse(**doc)


@router.get("/", response_model=list[CredentialResponse])
async def list_credentials(
    page: int = 1,
    page_size: int = 50,
):
    service = CredentialService()
    skip = (page - 1) * page_size
    items, _ = await service.list_credentials(skip=skip, limit=page_size)
    return [_doc_to_response(d) for d in items]


@router.post("/", response_model=CredentialResponse, status_code=status.HTTP_201_CREATED)
async def create_credential(data: CredentialCreate):
    service = CredentialService()
    cred_data = data.model_dump()
    # Strip secrets before storage (password / private_key stored via backend)
    cred_data.pop("password", None)
    cred_data.pop("private_key", None)
    doc = await service.create_credential(cred_data)
    return _doc_to_response(doc)


@router.delete("/{cred_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_credential(cred_id: str):
    service = CredentialService()
    existing = await service.get_credential(cred_id)
    if not existing:
        raise HTTPException(status_code=404, detail="Credential not found")
    await service.delete_credential(cred_id)
