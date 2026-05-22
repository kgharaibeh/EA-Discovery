import logging
from typing import Any

from scanner.normalizers.base import AbstractNormalizer

logger = logging.getLogger(__name__)


class LinuxNormalizer(AbstractNormalizer):
    """Normalizes Linux-specific collector output to the standard asset document format."""

    def normalize(self, raw_data: dict) -> dict:
        """Merge all collector outputs into a single normalized asset dict.

        Args:
            raw_data: Combined dict from all collectors keyed by collector name,
                      e.g. {"os": {...}, "ports": {...}, "services": {...}, ...}.

        Returns:
            A unified asset document in standard format.
        """
        asset: dict[str, Any] = {
            "os_family": "linux",
            "os_version": "",
            "hostname": "",
            "ip_addresses": [],
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

        # OS information
        os_data = raw_data.get("os", {})
        asset["os_version"] = os_data.get("os_version", "")
        asset["hostname"] = os_data.get("hostname", "")
        asset["ip_addresses"] = os_data.get("ip_addresses", [])
        if "kernel" in os_data:
            asset["kernel"] = os_data["kernel"]

        # Ports
        port_data = raw_data.get("ports", {})
        asset["open_ports"] = port_data.get("open_ports", [])
        asset["listening_services"] = port_data.get("listening_services", [])

        # Services
        service_data = raw_data.get("services", {})
        asset["running_services"] = service_data.get("running_services", [])

        # Network connections
        network_data = raw_data.get("network", {})
        asset["connections"] = network_data.get("connections", [])

        # Software
        software_data = raw_data.get("software", {})
        asset["installed_software"] = software_data.get("installed_software", [])

        # App servers
        appserver_data = raw_data.get("appserver", {})
        if appserver_data.get("app_server_type"):
            asset["app_server_type"] = appserver_data["app_server_type"]
            asset["app_server_version"] = appserver_data.get("app_server_version", "")
        asset["app_servers"] = appserver_data.get("app_servers", [])
        # Merge deployed artifacts from appserver detection
        asset["deployed_artifacts"].extend(appserver_data.get("deployed_artifacts", []))

        # Databases
        db_data = raw_data.get("database", {})
        if db_data.get("db_engine"):
            asset["db_engine"] = db_data["db_engine"]
            asset["db_version"] = db_data.get("db_version", "")
        asset["databases"] = db_data.get("databases", [])

        # Config parser (connection strings)
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

        # Deduplicate deployed artifacts by path
        asset["deployed_artifacts"] = self._deduplicate(
            asset["deployed_artifacts"], key="path"
        )
        # Deduplicate config files by path
        asset["config_files"] = self._deduplicate(
            asset["config_files"], key="path"
        )

        return asset

    @staticmethod
    def _deduplicate(items: list[dict], key: str) -> list[dict]:
        """Remove duplicate dicts from a list based on a key field."""
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
