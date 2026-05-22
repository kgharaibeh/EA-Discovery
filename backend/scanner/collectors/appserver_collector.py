import logging
import re

from scanner.collectors.base import AbstractCollector
from scanner.connectors.base import AbstractConnector

logger = logging.getLogger(__name__)

# Known process signatures for application server detection
APP_SERVER_SIGNATURES = {
    "weblogic": {
        "process_patterns": ["weblogic.Server", "weblogic.jar", "wls"],
        "common_paths": [
            "/opt/oracle/weblogic",
            "/opt/weblogic",
            "/u01/app/oracle/middleware",
        ],
    },
    "tomcat": {
        "process_patterns": ["catalina", "org.apache.catalina", "tomcat"],
        "common_paths": [
            "/opt/tomcat",
            "/usr/share/tomcat",
            "/var/lib/tomcat",
            "/opt/apache-tomcat",
        ],
    },
    "jboss": {
        "process_patterns": ["jboss", "wildfly", "org.jboss"],
        "common_paths": [
            "/opt/jboss",
            "/opt/wildfly",
            "/usr/share/wildfly",
        ],
    },
    "iis": {
        "process_patterns": ["w3wp.exe", "iisexpress"],
        "common_paths": [],
    },
    "apache_http": {
        "process_patterns": ["httpd", "apache2"],
        "common_paths": [
            "/etc/httpd",
            "/etc/apache2",
            "/opt/apache",
        ],
    },
    "nginx": {
        "process_patterns": ["nginx"],
        "common_paths": [
            "/etc/nginx",
            "/opt/nginx",
        ],
    },
}


class AppServerCollector(AbstractCollector):
    """Detects application servers (WebLogic, Tomcat, JBoss, IIS, Apache, Nginx)."""

    SUPPORTED_OS = {"linux", "windows", "aix", "solaris"}

    def supports_os(self, os_family: str) -> bool:
        return os_family.lower() in self.SUPPORTED_OS

    async def collect(self, connector: AbstractConnector, os_family: str) -> dict:
        os_family = os_family.lower()

        if os_family == "windows":
            return await self._collect_windows(connector)
        return await self._collect_unix(connector, os_family)

    async def _collect_unix(self, connector: AbstractConnector, os_family: str) -> dict:
        # Get running processes
        ps_result = await connector.execute("ps -eo args 2>/dev/null", timeout=15)
        process_lines = ps_result.stdout.splitlines() if ps_result.exit_code == 0 else []

        detected_servers: list[dict] = []

        for server_type, sig in APP_SERVER_SIGNATURES.items():
            if server_type == "iis":
                continue  # IIS is Windows-only

            # Check process patterns
            found_process = False
            matched_line = ""
            for line in process_lines:
                for pattern in sig["process_patterns"]:
                    if pattern.lower() in line.lower():
                        found_process = True
                        matched_line = line
                        break
                if found_process:
                    break

            # Check common paths
            found_path = ""
            for path in sig.get("common_paths", []):
                check = await connector.execute(f"test -d {path!r} && echo EXISTS", timeout=5)
                if check.exit_code == 0 and "EXISTS" in check.stdout:
                    found_path = path
                    break

            if found_process or found_path:
                server_info = await self._get_server_details(
                    connector, server_type, matched_line, found_path
                )
                detected_servers.append(server_info)

        if not detected_servers:
            return {"app_servers": []}

        # Return the primary server plus any others
        primary = detected_servers[0]
        return {
            "app_server_type": primary.get("type", ""),
            "app_server_version": primary.get("version", ""),
            "deployed_artifacts": primary.get("deployed_artifacts", []),
            "app_servers": detected_servers,
        }

    async def _collect_windows(self, connector: AbstractConnector) -> dict:
        detected_servers: list[dict] = []

        # Check for IIS
        iis_check = await connector.execute(
            "Get-Service W3SVC -ErrorAction SilentlyContinue | "
            "Select-Object Status | ConvertTo-Json -Compress",
            timeout=10,
        )
        if iis_check.exit_code == 0 and "Running" in iis_check.stdout:
            version_cmd = (
                "(Get-ItemProperty "
                "'HKLM:\\SOFTWARE\\Microsoft\\InetStp').VersionString"
            )
            ver_result = await connector.execute(version_cmd, timeout=10)
            detected_servers.append({
                "type": "iis",
                "version": ver_result.stdout.strip() if ver_result.exit_code == 0 else "",
                "deployed_artifacts": [],
            })

        # Check for Tomcat / Java app servers via processes
        proc_cmd = "Get-Process | Select-Object ProcessName, Path | ConvertTo-Json -Compress"
        proc_result = await connector.execute(proc_cmd, timeout=10)
        if proc_result.exit_code == 0 and proc_result.stdout.strip():
            import json
            try:
                processes = json.loads(proc_result.stdout)
                if isinstance(processes, dict):
                    processes = [processes]
                for proc in processes:
                    path = (proc.get("Path") or "").lower()
                    name = (proc.get("ProcessName") or "").lower()
                    for server_type, sig in APP_SERVER_SIGNATURES.items():
                        if server_type == "iis":
                            continue
                        for pattern in sig["process_patterns"]:
                            if pattern.lower() in name or pattern.lower() in path:
                                detected_servers.append({
                                    "type": server_type,
                                    "version": "",
                                    "deployed_artifacts": [],
                                })
                                break
            except json.JSONDecodeError:
                pass

        if not detected_servers:
            return {"app_servers": []}

        primary = detected_servers[0]
        return {
            "app_server_type": primary.get("type", ""),
            "app_server_version": primary.get("version", ""),
            "deployed_artifacts": primary.get("deployed_artifacts", []),
            "app_servers": detected_servers,
        }

    async def _get_server_details(
        self,
        connector: AbstractConnector,
        server_type: str,
        process_line: str,
        install_path: str,
    ) -> dict:
        """Extract version and deployed artifacts for a detected server."""
        info: dict = {"type": server_type, "version": "", "deployed_artifacts": []}

        if server_type == "tomcat":
            if install_path:
                ver_result = await connector.execute(
                    f"{install_path}/bin/catalina.sh version 2>/dev/null | head -5",
                    timeout=10,
                )
                if ver_result.exit_code == 0:
                    for line in ver_result.stdout.splitlines():
                        if "Server number" in line or "Server version" in line:
                            info["version"] = line.split(":", 1)[-1].strip()
                            break
                # Find deployed WARs
                webapps = await connector.execute(
                    f"ls {install_path}/webapps/*.war 2>/dev/null", timeout=10
                )
                if webapps.exit_code == 0:
                    info["deployed_artifacts"] = [
                        w.strip().rsplit("/", 1)[-1]
                        for w in webapps.stdout.splitlines()
                        if w.strip()
                    ]

        elif server_type == "weblogic":
            # Try to extract version from the process command line
            ver_match = re.search(r"weblogic[./](\d+\.\d+[\.\d]*)", process_line, re.IGNORECASE)
            if ver_match:
                info["version"] = ver_match.group(1)

        elif server_type == "jboss":
            if install_path:
                ver_result = await connector.execute(
                    f"{install_path}/bin/standalone.sh --version 2>/dev/null | head -3",
                    timeout=10,
                )
                if ver_result.exit_code == 0:
                    for line in ver_result.stdout.splitlines():
                        if "WildFly" in line or "JBoss" in line:
                            info["version"] = line.strip()
                            break

        elif server_type == "nginx":
            ver_result = await connector.execute("nginx -v 2>&1", timeout=10)
            if ver_result.exit_code == 0:
                info["version"] = ver_result.stdout.strip() or ver_result.stderr.strip()

        elif server_type == "apache_http":
            ver_result = await connector.execute(
                "httpd -v 2>/dev/null || apache2 -v 2>/dev/null", timeout=10
            )
            if ver_result.exit_code == 0:
                for line in ver_result.stdout.splitlines():
                    if "Server version" in line:
                        info["version"] = line.split(":", 1)[-1].strip()
                        break

        return info
