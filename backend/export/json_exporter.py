import json
from typing import Any


class JSONExporter:
    async def export(self, topology_data: dict) -> str:
        return json.dumps(topology_data, indent=2, default=str)
