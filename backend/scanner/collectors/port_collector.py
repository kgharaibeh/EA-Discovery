import json
import logging
import re

from scanner.collectors.base import AbstractCollector
from scanner.connectors.base import AbstractConnector

logger = logging.getLogger(__name__)


class PortCollector(AbstractCollector):
    """Collects information about open/listening ports on the target system."""

    SUPPORTED_OS = {"linux", "windows", "aix", "solaris"}

    def supports_os(self, os_family: str) -> bool:
        return os_family.lower() in self.SUPPORTED_OS

    async def collect(self, connector: AbstractConnector, os_family: str) -> dict:
        os_family = os_family.lower()
        dispatch = {
            "linux": self._collect_linux,
            "windows": self._collect_windows,
            "aix": self._collect_unix,
            "solaris": self._collect_unix,
        }
        handler = dispatch.get(os_family, self._collect_linux)
        return await handler(connector)

    async def _collect_linux(self, connector: AbstractConnector) -> dict:
        result = await connector.execute("ss -tlnp", timeout=15)
        if result.exit_code != 0:
            logger.warning("ss command failed, trying netstat")
            result = await connector.execute("netstat -tlnp 2>/dev/null", timeout=15)

        open_ports: list[dict] = []
        listening_services: list[dict] = []

        if result.exit_code == 0:
            for line in result.stdout.splitlines()[1:]:  # skip header
                parts = line.split()
                if len(parts) < 4:
                    continue

                # Parse local address:port
                local_addr = parts[3] if "ss" in result.stdout.splitlines()[0] else parts[3]
                addr, _, port_str = local_addr.rpartition(":")
                if not port_str.isdigit():
                    continue

                port = int(port_str)
                process = ""
                # Extract process name from ss output (users:(("name",pid=N,...)))
                for part in parts:
                    match = re.search(r'users:\(\("([^"]+)"', part)
                    if match:
                        process = match.group(1)
                        break

                entry = {
                    "port": port,
                    "protocol": "tcp",
                    "address": addr.strip("[]"),
                    "process": process,
                }
                open_ports.append(entry)
                if process:
                    listening_services.append({"port": port, "process": process})

        return {"open_ports": open_ports, "listening_services": listening_services}

    async def _collect_windows(self, connector: AbstractConnector) -> dict:
        cmd = (
            "Get-NetTCPConnection -State Listen | "
            "Select-Object LocalAddress, LocalPort, OwningProcess | "
            "ConvertTo-Json -Compress"
        )
        result = await connector.execute(cmd, timeout=15)

        open_ports: list[dict] = []
        listening_services: list[dict] = []

        if result.exit_code == 0 and result.stdout.strip():
            try:
                entries = json.loads(result.stdout)
                if isinstance(entries, dict):
                    entries = [entries]
                for entry in entries:
                    port_info = {
                        "port": entry.get("LocalPort", 0),
                        "protocol": "tcp",
                        "address": entry.get("LocalAddress", ""),
                        "pid": entry.get("OwningProcess", 0),
                    }
                    open_ports.append(port_info)
            except json.JSONDecodeError:
                logger.warning("Failed to parse Windows port data")

        return {"open_ports": open_ports, "listening_services": listening_services}

    async def _collect_unix(self, connector: AbstractConnector) -> dict:
        """Collect listening ports on AIX or Solaris using netstat."""
        result = await connector.execute("netstat -an | grep LISTEN", timeout=15)

        open_ports: list[dict] = []
        if result.exit_code == 0:
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) < 4:
                    continue
                # Parse the local address column (varies by OS)
                local_addr = parts[3] if len(parts) > 3 else parts[0]
                _, _, port_str = local_addr.rpartition(".")
                if port_str.isdigit():
                    open_ports.append({
                        "port": int(port_str),
                        "protocol": "tcp",
                        "address": local_addr.rpartition(".")[0],
                    })

        return {"open_ports": open_ports, "listening_services": []}
