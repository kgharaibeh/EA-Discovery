import json
import logging

from scanner.collectors.base import AbstractCollector
from scanner.connectors.base import AbstractConnector

logger = logging.getLogger(__name__)

# Common deployment directories to search for artifacts
UNIX_DEPLOY_PATHS = [
    "/opt/tomcat/webapps",
    "/opt/jboss/standalone/deployments",
    "/opt/wildfly/standalone/deployments",
    "/opt/weblogic",
    "/var/lib/tomcat/webapps",
    "/usr/share/tomcat/webapps",
    "/srv",
    "/opt/app",
]

WINDOWS_DEPLOY_PATHS = [
    "C:\\inetpub\\wwwroot",
    "C:\\Program Files\\Apache Software Foundation\\Tomcat\\webapps",
]

# Configuration file extensions to look for
CONFIG_EXTENSIONS = ("*.xml", "*.properties", "*.yml", "*.yaml", "*.json", "*.ini", "*.conf")

# Artifact extensions
ARTIFACT_EXTENSIONS = ("*.war", "*.jar", "*.ear")


class FilesystemCollector(AbstractCollector):
    """Finds deployed artifacts (WAR/JAR/EAR) and configuration files."""

    SUPPORTED_OS = {"linux", "windows", "aix", "solaris"}

    def supports_os(self, os_family: str) -> bool:
        return os_family.lower() in self.SUPPORTED_OS

    async def collect(self, connector: AbstractConnector, os_family: str) -> dict:
        os_family = os_family.lower()
        if os_family == "windows":
            return await self._collect_windows(connector)
        return await self._collect_unix(connector)

    async def _collect_unix(self, connector: AbstractConnector) -> dict:
        deployed_artifacts: list[dict] = []
        config_files: list[dict] = []

        for base_path in UNIX_DEPLOY_PATHS:
            # Check if path exists
            check = await connector.execute(f"test -d {base_path!r} && echo EXISTS", timeout=5)
            if check.exit_code != 0 or "EXISTS" not in check.stdout:
                continue

            # Find WAR/JAR/EAR artifacts
            artifact_cmd = (
                f"find {base_path!r} -type f "
                r"\( -name '*.war' -o -name '*.jar' -o -name '*.ear' \) "
                "-printf '%p|%s|%T@\\n' 2>/dev/null"
            )
            art_result = await connector.execute(artifact_cmd, timeout=15)
            if art_result.exit_code == 0:
                for line in art_result.stdout.splitlines():
                    parts = line.strip().split("|")
                    if len(parts) >= 2:
                        deployed_artifacts.append({
                            "path": parts[0],
                            "name": parts[0].rsplit("/", 1)[-1],
                            "size_bytes": int(parts[1]) if parts[1].isdigit() else 0,
                            "type": parts[0].rsplit(".", 1)[-1].upper(),
                        })

            # Find configuration files
            config_cmd = (
                f"find {base_path!r} -type f "
                r"\( -name '*.xml' -o -name '*.properties' -o -name '*.yml' "
                r"-o -name '*.yaml' -o -name '*.json' -o -name '*.ini' "
                r"-o -name '*.conf' \) "
                "-size -1M -printf '%p|%s\\n' 2>/dev/null"
            )
            cfg_result = await connector.execute(config_cmd, timeout=15)
            if cfg_result.exit_code == 0:
                for line in cfg_result.stdout.splitlines():
                    parts = line.strip().split("|")
                    if len(parts) >= 1 and parts[0]:
                        config_files.append({
                            "path": parts[0],
                            "name": parts[0].rsplit("/", 1)[-1],
                            "size_bytes": int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0,
                        })

        return {
            "deployed_artifacts": deployed_artifacts,
            "config_files": config_files,
        }

    async def _collect_windows(self, connector: AbstractConnector) -> dict:
        deployed_artifacts: list[dict] = []
        config_files: list[dict] = []

        for base_path in WINDOWS_DEPLOY_PATHS:
            # Find artifacts
            art_cmd = (
                f"Get-ChildItem -Path '{base_path}' -Recurse -Include *.war,*.jar,*.ear "
                "-ErrorAction SilentlyContinue | "
                "Select-Object FullName, Length, Name | ConvertTo-Json -Compress"
            )
            art_result = await connector.execute(art_cmd, timeout=15)
            if art_result.exit_code == 0 and art_result.stdout.strip():
                try:
                    items = json.loads(art_result.stdout)
                    if isinstance(items, dict):
                        items = [items]
                    for item in items:
                        name = item.get("Name", "")
                        deployed_artifacts.append({
                            "path": item.get("FullName", ""),
                            "name": name,
                            "size_bytes": item.get("Length", 0),
                            "type": name.rsplit(".", 1)[-1].upper() if "." in name else "",
                        })
                except json.JSONDecodeError:
                    pass

            # Find config files
            cfg_cmd = (
                f"Get-ChildItem -Path '{base_path}' -Recurse "
                "-Include *.xml,*.properties,*.yml,*.yaml,*.json,*.ini,*.conf,*.config "
                "-ErrorAction SilentlyContinue | "
                "Where-Object { $_.Length -lt 1MB } | "
                "Select-Object FullName, Length, Name | ConvertTo-Json -Compress"
            )
            cfg_result = await connector.execute(cfg_cmd, timeout=15)
            if cfg_result.exit_code == 0 and cfg_result.stdout.strip():
                try:
                    items = json.loads(cfg_result.stdout)
                    if isinstance(items, dict):
                        items = [items]
                    for item in items:
                        config_files.append({
                            "path": item.get("FullName", ""),
                            "name": item.get("Name", ""),
                            "size_bytes": item.get("Length", 0),
                        })
                except json.JSONDecodeError:
                    pass

        return {
            "deployed_artifacts": deployed_artifacts,
            "config_files": config_files,
        }
