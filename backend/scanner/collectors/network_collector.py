import json
import logging
import re

from scanner.collectors.base import AbstractCollector
from scanner.connectors.base import AbstractConnector

logger = logging.getLogger(__name__)


class NetworkCollector(AbstractCollector):
    """Collects active TCP connections for relationship mapping.

    This is a key collector -- its output feeds directly into
    relationship extraction to discover how assets communicate.
    """

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
        result = await connector.execute("ss -tnp", timeout=15)
        if result.exit_code != 0:
            result = await connector.execute("netstat -tnp 2>/dev/null", timeout=15)

        connections: list[dict] = []
        if result.exit_code == 0:
            for line in result.stdout.splitlines()[1:]:  # skip header
                parts = line.split()
                if len(parts) < 5:
                    continue

                state = parts[0] if parts[0] in ("ESTAB", "ESTABLISHED", "LISTEN") else ""
                if not state:
                    # ss format: State Recv-Q Send-Q Local Remote Process
                    if len(parts) >= 6:
                        state = parts[0]
                        local = parts[3]
                        remote = parts[4]
                        process_info = parts[5] if len(parts) > 5 else ""
                    else:
                        continue
                else:
                    local = parts[3]
                    remote = parts[4]
                    process_info = parts[5] if len(parts) > 5 else ""

                local_ip, _, local_port = local.rpartition(":")
                remote_ip, _, remote_port = remote.rpartition(":")

                process = ""
                pid = 0
                proc_match = re.search(r'users:\(\("([^"]+)",pid=(\d+)', process_info)
                if proc_match:
                    process = proc_match.group(1)
                    pid = int(proc_match.group(2))

                if local_port.isdigit() and remote_port.isdigit():
                    connections.append({
                        "local_ip": local_ip.strip("[]"),
                        "local_port": int(local_port),
                        "remote_ip": remote_ip.strip("[]"),
                        "remote_port": int(remote_port),
                        "state": state,
                        "process": process,
                        "pid": pid,
                    })

        return {"connections": connections}

    async def _collect_windows(self, connector: AbstractConnector) -> dict:
        cmd = (
            "Get-NetTCPConnection -State Established | "
            "Select-Object LocalAddress, LocalPort, RemoteAddress, "
            "RemotePort, OwningProcess | ConvertTo-Json -Compress"
        )
        result = await connector.execute(cmd, timeout=15)

        connections: list[dict] = []
        if result.exit_code == 0 and result.stdout.strip():
            try:
                entries = json.loads(result.stdout)
                if isinstance(entries, dict):
                    entries = [entries]
                for entry in entries:
                    pid = entry.get("OwningProcess", 0)
                    connections.append({
                        "local_ip": entry.get("LocalAddress", ""),
                        "local_port": entry.get("LocalPort", 0),
                        "remote_ip": entry.get("RemoteAddress", ""),
                        "remote_port": entry.get("RemotePort", 0),
                        "state": "ESTABLISHED",
                        "process": "",
                        "pid": pid,
                    })
            except json.JSONDecodeError:
                logger.warning("Failed to parse Windows network connection data")

        # Resolve PIDs to process names if we have connections
        if connections:
            pid_cmd = (
                "Get-Process | Select-Object Id, ProcessName | ConvertTo-Json -Compress"
            )
            pid_result = await connector.execute(pid_cmd, timeout=10)
            if pid_result.exit_code == 0 and pid_result.stdout.strip():
                try:
                    processes = json.loads(pid_result.stdout)
                    if isinstance(processes, dict):
                        processes = [processes]
                    pid_map = {p["Id"]: p["ProcessName"] for p in processes}
                    for conn in connections:
                        conn["process"] = pid_map.get(conn["pid"], "")
                except json.JSONDecodeError:
                    pass

        return {"connections": connections}

    async def _collect_unix(self, connector: AbstractConnector) -> dict:
        """Collect established connections on AIX or Solaris using netstat."""
        result = await connector.execute("netstat -an | grep ESTABLISHED", timeout=15)

        connections: list[dict] = []
        if result.exit_code == 0:
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) < 5:
                    continue

                local = parts[3] if len(parts) > 3 else ""
                remote = parts[4] if len(parts) > 4 else ""

                local_ip, _, local_port = local.rpartition(".")
                remote_ip, _, remote_port = remote.rpartition(".")

                if local_port.isdigit() and remote_port.isdigit():
                    connections.append({
                        "local_ip": local_ip,
                        "local_port": int(local_port),
                        "remote_ip": remote_ip,
                        "remote_port": int(remote_port),
                        "state": "ESTABLISHED",
                        "process": "",
                        "pid": 0,
                    })

        return {"connections": connections}
