from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse

from app.dependencies import get_asset_repo, get_relationship_repo
from app.repositories.asset_repo import AssetRepository
from app.repositories.relationship_repo import RelationshipRepository
from app.schemas.export import ExportRequest
from app.services.export_service import ExportService
from app.services.relationship_service import RelationshipService

router = APIRouter()


@router.post("/")
async def generate_export(
    request: ExportRequest,
    asset_repo: AssetRepository = Depends(get_asset_repo),
    rel_repo: RelationshipRepository = Depends(get_relationship_repo),
):
    rel_service = RelationshipService(rel_repo, asset_repo)
    export_service = ExportService(rel_service)

    if request.format == "drawio":
        content = await export_service.export_drawio(
            asset_types=request.asset_types,
            relationship_types=request.relationship_types,
        )
        return PlainTextResponse(
            content=content,
            media_type="application/xml",
            headers={"Content-Disposition": "attachment; filename=ea-topology.drawio"},
        )
    elif request.format == "csv":
        content = await export_service.export_csv(
            asset_types=request.asset_types,
        )
        return PlainTextResponse(
            content=content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=ea-topology.csv"},
        )
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported export format: {request.format}. Use 'drawio' or 'csv'.",
        )
