from fastapi import APIRouter

from app.api.v1 import scans, assets, relationships, credentials, dashboard, intelligence, drift, exports

api_router = APIRouter()

api_router.include_router(scans.router, prefix="/scans", tags=["Scans"])
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
api_router.include_router(relationships.router, prefix="/relationships", tags=["Relationships"])
api_router.include_router(credentials.router, prefix="/credentials", tags=["Credentials"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["Intelligence"])
api_router.include_router(drift.router, prefix="/drift", tags=["Drift"])
api_router.include_router(exports.router, prefix="/exports", tags=["Exports"])
