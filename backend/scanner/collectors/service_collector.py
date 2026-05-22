import json
import logging

from scanner.collectors.base import AbstractCollector
from scanner.connectors.base import AbstractConnector

logger = logging.getLogger(__name__)


class ServiceCollector(AbstractCollector):
    """Collects running services from the target system."""

    SUPPORTED_OS = {"linux", "windows", "aix", "solaris"}

    def supports_os(self, os_family: str) -> bool:
        return os_family.lower() in self.SUPPORTED_OS

    async def collect(self, connector: AbstractConnector, os_family: str) -> dict:
        os_family = os_family.lower()
        dispatch = {
            "linux": self._collect_linux,
            "windows": self._collect_windows,
            "aix": self._collect_aix,
            "solaris": self._collect_solaris,
        }
        handler = dispatch.get(os_family, self._collect_linux)
        return await handler(connector)

    async def _collect_linux(self, connector: AbstractConnector) -> dict:
        result = await connector.execute(
            "systemctl list-units --type=service --state=running --no-pager --plain",
            timeout=15,
        )

        services: list[dict] = []
        if result.exit_code == 0:
            for line in result.stdout.splitlines():
                parts = line.split(None, 4)
                if len(parts) >= 4 and parts[0].endswith(".service"):
                    services.append({
                        "name": parts[0].replace(".service", ""),
                        "unit": parts[0],
                        "load": parts[1],
                        "active": parts[2],
                        "sub": parts[3],
                        "description": parts[4] if len(parts) > 4 else "",
                    })
        else:
            # Fallback for systems without systemd
            result = await connector.execute(
                "service --status-all 2>/dev/null | grep '\\[ + \\]'", timeout=15
            )
            if result.exit_code == 0:
                for line in result.stdout.splitlines():
                    name = line.strip().split("]")[-1].strip()
                    if name:
                        services.append({"name": name, "active": "running"})

        return {"running_services": services}

    async def _collect_windows(self, connector: AbstractConnector) -> dict:
        cmd = (
            "Get-Service | Where-Object {$_.Status -eq 'Running'} | "
            "Select-Object Name, DisplayName | ConvertTo-Json -Compress"
        )
        result = await connector.execute(cmd, timeout=15)

        services: list[dict] = []
        if result.exit_code == 0 and result.stdout.strip():
            try:
                parsed = json.loads(result.stdout)
                if isinstance(parsed, dict):
                    parsed = [parsed]
                for svc in parsed:
                    services.append({
                        "name": svc.get("Name", ""),
                        "display_name": svc.get("DisplayName", ""),
                    })
            except json.JSONDecodeError:
                logger.warning("Failed to parse Windows service data")

        return {"running_services": services}

    async def _collect_aix(self, connector: AbstractConnector) -> dict:
        result = await connector.execute("lssrc -a", timeout=15)

        services: list[dict] = []
        if result.exit_code == 0:
            for line in result.stdout.splitlines()[1:]:  # skip header
                parts = line.split()
                if len(parts) >= 3 and parts[-1].lower() == "active":
                    services.append({
                        "name": parts[0],
                        "group": parts[1] if len(parts) > 3 else "",
                        "pid": parts[-2] if len(parts) > 3 else "",
                        "status": "active",
                    })

        return {"running_services": services}

    async def _collect_solaris(self, connector: AbstractConnector) -> dict:
        result = await connector.execute(
            "svcs -a 2>/dev/null | grep online", timeout=15
        )

        services: list[dict] = []
        if result.exit_code == 0:
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 3:
                    services.append({
                        "name": parts[-1],
                        "state": parts[0],
                    })

        return {"running_services": services}
