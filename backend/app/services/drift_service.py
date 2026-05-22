from datetime import datetime

from app.repositories.drift_repo import DriftRepository


class DriftService:
    def __init__(self, drift_repo: DriftRepository):
        self.drift_repo = drift_repo

    async def detect_drift(self, current_asset: dict, previous_asset: dict | None, scan_id: str) -> list[dict]:
        if not previous_asset:
            return []

        events: list[dict] = []
        fields_to_compare = [
            ("open_ports", "port_change", self._compare_ports),
            ("running_services", "service_change", self._compare_list),
            ("installed_software", "software_change", self._compare_list),
            ("listening_services", "listener_change", self._compare_list),
            ("config_files", "config_change", self._compare_list),
        ]

        for field, drift_type, comparator in fields_to_compare:
            prev_val = previous_asset.get(field, [])
            curr_val = current_asset.get(field, [])
            if comparator(prev_val, curr_val):
                event = {
                    "_id": self.drift_repo.new_id(),
                    "asset_id": current_asset["_id"],
                    "scan_id": scan_id,
                    "previous_scan_id": previous_asset.get("scan_id", ""),
                    "drift_type": drift_type,
                    "field_path": field,
                    "previous_value": prev_val,
                    "current_value": curr_val,
                    "severity": self._assess_severity(drift_type),
                    "detected_at": datetime.utcnow(),
                    "acknowledged": False,
                }
                await self.drift_repo.insert(event)
                events.append(event)

        return events

    async def list_events(self, asset_id: str | None = None, severity: str | None = None, skip: int = 0, limit: int = 50) -> tuple[list[dict], int]:
        query: dict = {}
        if asset_id:
            query["asset_id"] = asset_id
        if severity:
            query["severity"] = severity
        items = await self.drift_repo.find_many(query, skip=skip, limit=limit, sort=[("detected_at", -1)])
        total = await self.drift_repo.count(query)
        return items, total

    async def acknowledge(self, event_id: str) -> bool:
        return await self.drift_repo.update(event_id, {"acknowledged": True})

    @staticmethod
    def _compare_ports(prev: list, curr: list) -> bool:
        prev_set = {(p.get("port"), p.get("protocol")) for p in prev}
        curr_set = {(p.get("port"), p.get("protocol")) for p in curr}
        return prev_set != curr_set

    @staticmethod
    def _compare_list(prev: list, curr: list) -> bool:
        return len(prev) != len(curr) or prev != curr

    @staticmethod
    def _assess_severity(drift_type: str) -> str:
        critical_types = {"port_change", "listener_change"}
        warning_types = {"service_change", "software_change"}
        if drift_type in critical_types:
            return "warning"
        if drift_type in warning_types:
            return "info"
        return "info"
