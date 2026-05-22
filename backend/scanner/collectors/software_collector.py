import json
import logging

from scanner.collectors.base import AbstractCollector
from scanner.connectors.base import AbstractConnector

logger = logging.getLogger(__name__)


class SoftwareCollector(AbstractCollector):
    """Collects installed software packages from the target system."""

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
        software: list[dict] = []

        # Try RPM-based systems first
        result = await connector.execute(
            "rpm -qa --qf '%{NAME}|%{VERSION}\\n' 2>/dev/null", timeout=30
        )
        if result.exit_code == 0 and result.stdout.strip():
            for line in result.stdout.splitlines():
                parts = line.strip().split("|", 1)
                if len(parts) == 2:
                    software.append({"name": parts[0], "version": parts[1]})
        else:
            # Try dpkg for Debian-based systems
            result = await connector.execute(
                "dpkg -l 2>/dev/null | grep '^ii'", timeout=30
            )
            if result.exit_code == 0:
                for line in result.stdout.splitlines():
                    parts = line.split()
                    if len(parts) >= 3:
                        software.append({"name": parts[1], "version": parts[2]})

        return {"installed_software": software}

    async def _collect_windows(self, connector: AbstractConnector) -> dict:
        cmd = (
            "Get-CimInstance -ClassName Win32_Product | "
            "Select-Object Name, Version | ConvertTo-Json -Compress"
        )
        result = await connector.execute(cmd, timeout=60)

        software: list[dict] = []
        if result.exit_code == 0 and result.stdout.strip():
            try:
                parsed = json.loads(result.stdout)
                if isinstance(parsed, dict):
                    parsed = [parsed]
                for item in parsed:
                    name = item.get("Name", "")
                    if name:
                        software.append({
                            "name": name,
                            "version": item.get("Version", ""),
                        })
            except json.JSONDecodeError:
                logger.warning("Failed to parse Windows software data")

        # Also check Programs and Features via registry as a supplement
        reg_cmd = (
            "Get-ItemProperty "
            "'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*' | "
            "Where-Object { $_.DisplayName } | "
            "Select-Object DisplayName, DisplayVersion | "
            "ConvertTo-Json -Compress"
        )
        reg_result = await connector.execute(reg_cmd, timeout=30)
        if reg_result.exit_code == 0 and reg_result.stdout.strip():
            try:
                parsed = json.loads(reg_result.stdout)
                if isinstance(parsed, dict):
                    parsed = [parsed]
                existing_names = {s["name"] for s in software}
                for item in parsed:
                    name = item.get("DisplayName", "")
                    if name and name not in existing_names:
                        software.append({
                            "name": name,
                            "version": item.get("DisplayVersion", ""),
                        })
            except json.JSONDecodeError:
                pass

        return {"installed_software": software}

    async def _collect_aix(self, connector: AbstractConnector) -> dict:
        result = await connector.execute("lslpp -l 2>/dev/null", timeout=30)

        software: list[dict] = []
        if result.exit_code == 0:
            for line in result.stdout.splitlines()[1:]:  # skip header
                parts = line.split()
                if len(parts) >= 2:
                    software.append({"name": parts[0], "version": parts[1]})

        return {"installed_software": software}

    async def _collect_solaris(self, connector: AbstractConnector) -> dict:
        result = await connector.execute("pkginfo -l 2>/dev/null", timeout=30)

        software: list[dict] = []
        if result.exit_code == 0:
            current: dict = {}
            for line in result.stdout.splitlines():
                if line.strip().startswith("PKGINST:"):
                    if current:
                        software.append(current)
                    current = {"name": line.split(":", 1)[1].strip(), "version": ""}
                elif line.strip().startswith("VERSION:"):
                    current["version"] = line.split(":", 1)[1].strip()
            if current:
                software.append(current)

        return {"installed_software": software}
