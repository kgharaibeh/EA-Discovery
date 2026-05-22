import logging
from typing import Any

from scanner.normalizers.base import AbstractNormalizer

logger = logging.getLogger(__name__)


class UnixNormalizer(AbstractNormalizer):
    """Normalizes AIX and Solaris output to the standard asset document format.

    AIX and Solaris share many similarities with Linux but have different
    command output formats that need special handling.
    """

    def normalize(self, raw_data: dict) -> dict:
        """Merge all collector outputs into a single normalized asset dict.

        Args:
            raw_data: Combined dict from all collectors keyed by collector name.

        Returns:
            A unified asset document in standard format.
        """
        os_data = raw_data.get("os", {})
        os_family = os_data.get("os_family", "unix")

        asset: dict[str, Any] = {
            "os_family": os_family,
            "os_version": os_data.get("os_version", ""),
            "hostname": os_data.get("hostname", ""),
            "ip_addresses": os_data.get("ip_addresses", []),
            "open_ports": [],
            "listening_services": [],
            "running_services": [],
            "connections": [],
            "installed_software": [],
            "app_servers": [],
            "databases": [],
            "deployed_artifacts": [],
            "config_files": [],
            "parsed_connections": [],
            "local_users": [],
            "active_sessions": [],
        }

        if "kernel" in os_data:
            asset["kernel"] = os_data["kernel"]

        # Ports -- AIX/Solaris use dotted notation (addr.port) instead of colon
        port_data = raw_data.get("ports", {})
        asset["open_ports"] = self._normalize_ports(port_data.get("open_ports", []))
        asset["listening_services"] = port_data.get("listening_services", [])

        # Services -- normalize AIX lssrc / Solaris svcs output
        service_data = raw_data.get("services", {})
        asset["running_services"] = self._normalize_services(
            service_data.get("running_services", [])
        )

        # Network connections
        network_data = raw_data.get("network", {})
        asset["connections"] = self._normalize_connections(
            network_data.get("connections", [])
        )

        # Software -- AIX lslpp / Solaris pkginfo
        software_data = raw_data.get("software", {})
        asset["installed_software"] = software_data.get("installed_software", [])

        # App servers
        appserver_data = raw_data.get("appserver", {})
        if appserver_data.get("app_server_type"):
            asset["app_server_type"] = appserver_data["app_server_type"]
            asset["app_server_version"] = appserver_data.get("app_server_version", "")
        asset["app_servers"] = appserver_data.get("app_servers", [])
        asset["deployed_artifacts"].extend(appserver_data.get("deployed_artifacts", []))

        # Databases
        db_data = raw_data.get("database", {})
        if db_data.get("db_engine"):
            asset["db_engine"] = db_data["db_engine"]
            asset["db_version"] = db_data.get("db_version", "")
        asset["databases"] = db_data.get("databases", [])

        # Config parser
        config_data = raw_data.get("config", {})
        asset["parsed_connections"] = config_data.get("parsed_connections", [])
        asset["config_files"].extend(config_data.get("config_files", []))

        # Filesystem
        fs_data = raw_data.get("filesystem", {})
        asset["deployed_artifacts"].extend(fs_data.get("deployed_artifacts", []))
        asset["config_files"].extend(fs_data.get("config_files", []))

        # Users
        user_data = raw_data.get("users", {})
        asset["local_users"] = user_data.get("local_users", [])
        asset["active_sessions"] = user_data.get("active_sessions", [])

        # Deduplicate
        asset["deployed_artifacts"] = self._deduplicate(
            asset["deployed_artifacts"], key="path"
        )
        asset["config_files"] = self._deduplicate(
            asset["config_files"], key="path"
        )

        return asset

    @staticmethod
    def _normalize_ports(ports: list[dict]) -> list[dict]:
        """Normalize port entries from AIX/Solaris netstat output."""
        normalized: list[dict] = []
        for port in ports:
            # AIX/Solaris netstat uses dot-separated addr.port format
            address = port.get("address", "")
            # Strip leading asterisks or wildcards
            if address in ("*", "0.0.0.0", "::"):
                address = "0.0.0.0"
            normalized.append({
                "port": port.get("port", 0),
                "protocol": port.get("protocol", "tcp"),
                "address": address,
            })
        return normalized

    @staticmethod
    def _normalize_services(services: list[dict]) -> list[dict]:
        """Normalize service entries from lssrc (AIX) or svcs (Solaris)."""
        normalized: list[dict] = []
        for svc in services:
            normalized.append({
                "name": svc.get("name", ""),
                "group": svc.get("group", ""),
                "status": svc.get("status", svc.get("state", "")),
                "active": "running",
            })
        return normalized

    @staticmethod
    def _normalize_connections(connections: list[dict]) -> list[dict]:
        """Normalize connection entries from AIX/Solaris netstat."""
        normalized: list[dict] = []
        for conn in connections:
            normalized.append({
                "local_ip": conn.get("local_ip", ""),
                "local_port": conn.get("local_port", 0),
                "remote_ip": conn.get("remote_ip", ""),
                "remote_port": conn.get("remote_port", 0),
                "state": conn.get("state", "ESTABLISHED"),
                "process": conn.get("process", ""),
                "pid": conn.get("pid", 0),
            })
        return normalized

    @staticmethod
    def _deduplicate(items: list[dict], key: str) -> list[dict]:
        seen: set[str] = set()
        unique: list[dict] = []
        for item in items:
            val = item.get(key, "")
            if val and val not in seen:
                seen.add(val)
                unique.append(item)
            elif not val:
                unique.append(item)
        return unique
