from collections import defaultdict
from traffic.plugins.base import RawFlow


class HTTPAnalyzer:
    def analyze(self, flows: list[RawFlow]) -> list[dict]:
        endpoints: dict[str, dict] = {}

        for flow in flows:
            if flow.protocol != "http" or not flow.path:
                continue

            normalized_path = self._normalize_path(flow.path)
            key = f"{flow.method or 'GET'}:{flow.dst_ip}:{flow.dst_port}{normalized_path}"

            if key not in endpoints:
                endpoints[key] = {
                    "method": flow.method or "GET",
                    "host": flow.dst_ip,
                    "port": flow.dst_port,
                    "path": normalized_path,
                    "content_types": set(),
                    "status_codes": set(),
                    "consumers": set(),
                    "request_count": 0,
                    "total_bytes": 0,
                }

            ep = endpoints[key]
            ep["request_count"] += 1
            ep["total_bytes"] += flow.bytes_transferred
            ep["consumers"].add(f"{flow.src_ip}:{flow.src_port}")
            if flow.content_type:
                ep["content_types"].add(flow.content_type)
            if flow.status_code:
                ep["status_codes"].add(flow.status_code)

        result = []
        for ep in endpoints.values():
            result.append({
                "method": ep["method"],
                "host": ep["host"],
                "port": ep["port"],
                "path": ep["path"],
                "content_types": list(ep["content_types"]),
                "status_codes": sorted(ep["status_codes"]),
                "consumer_count": len(ep["consumers"]),
                "consumers": list(ep["consumers"])[:20],
                "request_count": ep["request_count"],
                "total_bytes": ep["total_bytes"],
            })
        return result

    @staticmethod
    def _normalize_path(path: str) -> str:
        parts = path.split("/")
        normalized = []
        for part in parts:
            if part.isdigit() or len(part) > 20:
                normalized.append("{id}")
            else:
                normalized.append(part)
        return "/".join(normalized)
