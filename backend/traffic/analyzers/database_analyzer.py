from traffic.plugins.base import RawFlow

DB_PORT_MAP = {
    1521: "oracle",
    1433: "sqlserver",
    3306: "mysql",
    5432: "postgresql",
    27017: "mongodb",
    6379: "redis",
    9042: "cassandra",
}


class DatabaseAnalyzer:
    def analyze(self, flows: list[RawFlow]) -> list[dict]:
        db_connections: dict[str, dict] = {}

        for flow in flows:
            db_type = DB_PORT_MAP.get(flow.dst_port)
            if not db_type:
                continue

            key = f"{flow.dst_ip}:{flow.dst_port}"
            if key not in db_connections:
                db_connections[key] = {
                    "host": flow.dst_ip,
                    "port": flow.dst_port,
                    "db_type": db_type,
                    "protocol": f"{db_type}_wire",
                    "clients": set(),
                    "request_count": 0,
                    "total_bytes": 0,
                }

            conn = db_connections[key]
            conn["clients"].add(flow.src_ip)
            conn["request_count"] += 1
            conn["total_bytes"] += flow.bytes_transferred

        result = []
        for conn in db_connections.values():
            result.append({
                "host": conn["host"],
                "port": conn["port"],
                "db_type": conn["db_type"],
                "protocol": conn["protocol"],
                "client_count": len(conn["clients"]),
                "clients": list(conn["clients"]),
                "request_count": conn["request_count"],
                "total_bytes": conn["total_bytes"],
            })
        return result
