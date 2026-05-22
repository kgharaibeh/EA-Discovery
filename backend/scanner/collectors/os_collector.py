import logging
import re

from scanner.collectors.base import AbstractCollector
from scanner.connectors.base import AbstractConnector

logger = logging.getLogger(__name__)


class OSCollector(AbstractCollector):
    """Detects OS family, version, hostname, and IP addresses."""

    SUPPORTED_OS = {"linux", "windows", "aix", "solaris", "unknown"}

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
        handler = dispatch.get(os_family, self._collect_generic)
        return await handler(connector)

    async def _collect_linux(self, connector: AbstractConnector) -> dict:
        result: dict = {"os_family": "linux", "os_version": "", "hostname": "", "ip_addresses": []}

        # OS release info
        os_release = await connector.execute("cat /etc/os-release 2>/dev/null", timeout=10)
        if os_release.exit_code == 0:
            for line in os_release.stdout.splitlines():
                if line.startswith("PRETTY_NAME="):
                    result["os_version"] = line.split("=", 1)[1].strip().strip('"')
                    break

        # Kernel info
        uname = await connector.execute("uname -a", timeout=10)
        if uname.exit_code == 0:
            result["kernel"] = uname.stdout.strip()

        # Hostname
        hostname = await connector.execute("hostname", timeout=10)
        if hostname.exit_code == 0:
            result["hostname"] = hostname.stdout.strip()

        # IP addresses
        ip_result = await connector.execute(
            "ip -4 addr show | grep -oP 'inet \\K[\\d.]+'", timeout=10
        )
        if ip_result.exit_code == 0:
            result["ip_addresses"] = [
                ip.strip() for ip in ip_result.stdout.splitlines() if ip.strip()
            ]

        return result

    async def _collect_windows(self, connector: AbstractConnector) -> dict:
        result: dict = {"os_family": "windows", "os_version": "", "hostname": "", "ip_addresses": []}

        os_ver = await connector.execute(
            "[System.Environment]::OSVersion | Select-Object -ExpandProperty VersionString",
            timeout=10,
        )
        if os_ver.exit_code == 0:
            result["os_version"] = os_ver.stdout.strip()

        hostname = await connector.execute("$env:COMPUTERNAME", timeout=10)
        if hostname.exit_code == 0:
            result["hostname"] = hostname.stdout.strip()

        ip_cmd = (
            "Get-NetIPAddress -AddressFamily IPv4 | "
            "Where-Object { $_.IPAddress -ne '127.0.0.1' } | "
            "Select-Object -ExpandProperty IPAddress"
        )
        ip_result = await connector.execute(ip_cmd, timeout=10)
        if ip_result.exit_code == 0:
            result["ip_addresses"] = [
                ip.strip() for ip in ip_result.stdout.splitlines() if ip.strip()
            ]

        return result

    async def _collect_aix(self, connector: AbstractConnector) -> dict:
        result: dict = {"os_family": "aix", "os_version": "", "hostname": "", "ip_addresses": []}

        oslevel = await connector.execute("oslevel -s", timeout=10)
        if oslevel.exit_code == 0:
            result["os_version"] = f"AIX {oslevel.stdout.strip()}"

        uname = await connector.execute("uname -a", timeout=10)
        if uname.exit_code == 0:
            result["kernel"] = uname.stdout.strip()

        hostname = await connector.execute("hostname", timeout=10)
        if hostname.exit_code == 0:
            result["hostname"] = hostname.stdout.strip()

        ip_result = await connector.execute(
            "ifconfig -a | grep 'inet ' | awk '{print $2}'", timeout=10
        )
        if ip_result.exit_code == 0:
            result["ip_addresses"] = [
                ip.strip() for ip in ip_result.stdout.splitlines()
                if ip.strip() and ip.strip() != "127.0.0.1"
            ]

        return result

    async def _collect_solaris(self, connector: AbstractConnector) -> dict:
        result: dict = {"os_family": "solaris", "os_version": "", "hostname": "", "ip_addresses": []}

        release = await connector.execute("cat /etc/release 2>/dev/null | head -1", timeout=10)
        if release.exit_code == 0:
            result["os_version"] = release.stdout.strip()

        uname = await connector.execute("uname -a", timeout=10)
        if uname.exit_code == 0:
            result["kernel"] = uname.stdout.strip()

        hostname = await connector.execute("hostname", timeout=10)
        if hostname.exit_code == 0:
            result["hostname"] = hostname.stdout.strip()

        ip_result = await connector.execute(
            "ifconfig -a | grep 'inet ' | awk '{print $2}'", timeout=10
        )
        if ip_result.exit_code == 0:
            result["ip_addresses"] = [
                ip.strip() for ip in ip_result.stdout.splitlines()
                if ip.strip() and ip.strip() != "127.0.0.1"
            ]

        return result

    async def _collect_generic(self, connector: AbstractConnector) -> dict:
        """Fallback collector that attempts Linux-style commands first."""
        logger.warning("Unknown OS family, attempting generic collection")
        return await self._collect_linux(connector)
