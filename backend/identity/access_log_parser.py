import re
from collections import defaultdict


class AccessLogParser:
    APACHE_PATTERN = re.compile(
        r'(?P<ip>\S+) \S+ (?P<user>\S+) \[(?P<time>[^\]]+)\] '
        r'"(?P<method>\S+) (?P<path>\S+) \S+" (?P<status>\d+) (?P<size>\S+)'
    )

    IIS_PATTERN = re.compile(
        r'(?P<date>\S+) (?P<time>\S+) \S+ (?P<method>\S+) (?P<path>\S+) \S+ '
        r'\S+ (?P<ip>\S+) (?P<user>\S+) (?P<status>\d+)'
    )

    def parse_apache_log(self, content: str) -> list[dict]:
        entries = []
        for line in content.strip().split("\n"):
            match = self.APACHE_PATTERN.match(line)
            if match:
                entries.append({
                    "ip": match.group("ip"),
                    "user": match.group("user"),
                    "method": match.group("method"),
                    "path": match.group("path"),
                    "status": int(match.group("status")),
                })
        return entries

    def parse_iis_log(self, content: str) -> list[dict]:
        entries = []
        for line in content.strip().split("\n"):
            if line.startswith("#"):
                continue
            match = self.IIS_PATTERN.match(line)
            if match:
                entries.append({
                    "ip": match.group("ip"),
                    "user": match.group("user"),
                    "method": match.group("method"),
                    "path": match.group("path"),
                    "status": int(match.group("status")),
                })
        return entries

    def aggregate_user_access(self, entries: list[dict]) -> list[dict]:
        user_stats: dict[str, dict] = defaultdict(lambda: {
            "request_count": 0,
            "paths": set(),
            "ips": set(),
            "methods": set(),
        })

        for entry in entries:
            user = entry.get("user", "-")
            if user == "-":
                continue
            stats = user_stats[user]
            stats["request_count"] += 1
            stats["paths"].add(entry.get("path", ""))
            stats["ips"].add(entry.get("ip", ""))
            stats["methods"].add(entry.get("method", ""))

        result = []
        for user, stats in user_stats.items():
            result.append({
                "user": user,
                "request_count": stats["request_count"],
                "unique_paths": len(stats["paths"]),
                "source_ips": list(stats["ips"]),
                "methods": list(stats["methods"]),
            })
        return sorted(result, key=lambda x: x["request_count"], reverse=True)
