from collections import defaultdict

from traffic.plugins.base import RawFlow

WELL_KNOWN_PORTS = {
    21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp",
    53: "dns", 80: "http", 110: "pop3", 143: "imap",
    389: "ldap", 443: "https", 636: "ldaps",
    993: "imaps", 995: "pop3s",
    1521: "oracle", 1433: "mssql", 3306: "mysql",
    5432: "postgresql", 6379: "redis", 8080: "http-alt",
    8443: "https-alt", 9090: "http-alt", 27017: "mongodb",
}


class GenericAnalyzer:
    def analyze(self, flows: list[RawFlow]) -> list[dict]:
        connections: dict[str, dict] = {}

        for flow in flows:
            key = f"{flow.src_ip}->{flow.dst_ip}:{flow.dst_port}"
            if key not in connections:
                protocol = WELL_KNOWN_PORTS.get(flow.dst_port, "unknown")
                connections[key] = {
                    "src_ip": flow.src_ip,
                    "dst_ip": flow.dst_ip,
                    "dst_port": flow.dst_port,
                    "protocol": protocol,
                    "request_count": 0,
                    "total_bytes": 0,
                }

            connections[key]["request_count"] += 1
            connections[key]["total_bytes"] += flow.bytes_transferred

        return list(connections.values())
