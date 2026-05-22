from app.repositories.asset_repo import AssetRepository
from app.repositories.relationship_repo import RelationshipRepository
from app.repositories.scan_repo import ScanRepository
from app.repositories.drift_repo import DriftRepository


def get_asset_repo() -> AssetRepository:
    return AssetRepository()


def get_relationship_repo() -> RelationshipRepository:
    return RelationshipRepository()


def get_scan_repo() -> ScanRepository:
    return ScanRepository()


def get_drift_repo() -> DriftRepository:
    return DriftRepository()
