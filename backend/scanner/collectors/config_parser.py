import logging
import re
from typing import Optional

from scanner.collectors.base import AbstractCollector
from scanner.connectors.base import AbstractConnector
from scanner.parsers.connection_string import ConnectionStringParser
from scanner.parsers.xml_config import XmlConfigParser
from scanner.parsers.properties import PropertiesParser

logger = logging.getLogger(__name__)

# Known configuration directories to search
LINUX_CONFIG_PATHS = [
    "/opt/tomcat/conf",
    "/opt/tomcat/webapps",
    "/opt/weblogic",
    "/opt/jboss/standalone/configuration",
    "/opt/wildfly/standalone/configuration",
    "/etc/httpd/conf",
    "/etc/apache2",
    "/etc/nginx",
    "/opt/app",
    "/srv",
    "/var/lib",
]

WINDOWS_CONFIG_PATHS = [
    "C:\\inetpub",
    "C:\\Program Files\\Apache Software Foundation",
    "C:\\Program Files\\Apache Group",
]


class ConfigParserCollector(AbstractCollector):
    """Searches known config directories and parses connection strings.

    This is a key collector for relationship mapping -- it discovers
    how applications connect to databases and other services by parsing
    configuration files for JDBC URLs, ODBC strings, Spring datasource
    properties, and XML resource references.
    """

    SUPPORTED_OS = {"linux", "windows", "aix", "solaris"}

    def __init__(self) -> None:
        self._conn_parser = ConnectionStringParser()
        self._xml_parser = XmlConfigParser()
        self._props_parser = PropertiesParser()

    def supports_os(self, os_family: str) -> bool:
        return os_family.lower() in self.SUPPORTED_OS

    async def collect(self, connector: AbstractConnector, os_family: str) -> dict:
        os_family = os_family.lower()
        config_files: list[dict] = []
        parsed_connections: list[dict] = []

        if os_family == "windows":
            search_paths = WINDOWS_CONFIG_PATHS
        else:
            search_paths = LINUX_CONFIG_PATHS

        # Find configuration files in known paths
        for base_path in search_paths:
            found_files = await self._find_config_files(connector, base_path, os_family)
            for file_info in found_files:
                config_files.append(file_info)
                # Read and parse each config file
                connections = await self._parse_config_file(
                    connector, file_info["path"], file_info["type"]
                )
                parsed_connections.extend(connections)

        return {
            "config_files": config_files,
            "parsed_connections": parsed_connections,
        }

    async def _find_config_files(
        self, connector: AbstractConnector, base_path: str, os_family: str
    ) -> list[dict]:
        """Find configuration files in a directory tree."""
        files: list[dict] = []

        if os_family == "windows":
            cmd = (
                f"Get-ChildItem -Path '{base_path}' -Recurse -Include "
                "*.xml,*.properties,*.yml,*.yaml,*.json,*.config "
                "-ErrorAction SilentlyContinue | "
                "Select-Object FullName, Length | ConvertTo-Json -Compress"
            )
        else:
            cmd = (
                f"find {base_path!r} -type f "
                r"\( -name '*.xml' -o -name '*.properties' -o -name '*.yml' "
                r"-o -name '*.yaml' -o -name '*.json' -o -name '*.conf' \) "
                "-size -1M 2>/dev/null"
            )

        result = await connector.execute(cmd, timeout=15)
        if result.exit_code != 0 or not result.stdout.strip():
            return files

        if os_family == "windows":
            import json
            try:
                parsed = json.loads(result.stdout)
                if isinstance(parsed, dict):
                    parsed = [parsed]
                for item in parsed:
                    path = item.get("FullName", "")
                    files.append({
                        "path": path,
                        "size": item.get("Length", 0),
                        "type": self._classify_config(path),
                    })
            except json.JSONDecodeError:
                pass
        else:
            for line in result.stdout.splitlines():
                path = line.strip()
                if path:
                    files.append({
                        "path": path,
                        "type": self._classify_config(path),
                    })

        return files

    def _classify_config(self, path: str) -> str:
        """Classify a config file by its name/extension."""
        lower = path.lower()
        if "web.xml" in lower:
            return "web_xml"
        if "server.xml" in lower:
            return "server_xml"
        if "application.properties" in lower or "application.yml" in lower:
            return "spring_config"
        if "weblogic" in lower and lower.endswith(".xml"):
            return "weblogic_config"
        if lower.endswith(".properties"):
            return "properties"
        if lower.endswith((".yml", ".yaml")):
            return "yaml"
        if lower.endswith(".xml"):
            return "xml"
        if lower.endswith(".json"):
            return "json"
        if lower.endswith((".conf", ".config")):
            return "config"
        return "unknown"

    async def _parse_config_file(
        self, connector: AbstractConnector, path: str, file_type: str
    ) -> list[dict]:
        """Read and parse a config file, extracting connection information."""
        try:
            content = await connector.read_file(path, max_bytes=524_288)
        except (FileNotFoundError, RuntimeError) as exc:
            logger.debug("Cannot read config file %s: %s", path, exc)
            return []

        connections: list[dict] = []

        # Look for JDBC URLs in any file
        jdbc_urls = re.findall(r'jdbc:[a-zA-Z]+:[^\s"\'<>]+', content)
        for url in jdbc_urls:
            parsed = self._conn_parser.parse_jdbc(url)
            if parsed:
                parsed["source_file"] = path
                connections.append(parsed)

        # Look for ODBC connection strings
        odbc_strings = re.findall(
            r'(?:Server|Data Source)=[^;]+;[^\n"\']+', content, re.IGNORECASE
        )
        for odbc in odbc_strings:
            parsed = self._conn_parser.parse_odbc(odbc)
            if parsed:
                parsed["source_file"] = path
                connections.append(parsed)

        # Type-specific parsing
        if file_type == "web_xml":
            refs = self._xml_parser.parse_web_xml(content)
            for ref in refs:
                ref["source_file"] = path
                connections.append(ref)

        elif file_type == "server_xml":
            datasources = self._xml_parser.parse_server_xml(content)
            for ds in datasources:
                ds["source_file"] = path
                connections.append(ds)

        elif file_type == "weblogic_config":
            jndi_sources = self._xml_parser.parse_weblogic_config(content)
            for ds in jndi_sources:
                ds["source_file"] = path
                connections.append(ds)

        elif file_type == "spring_config":
            if file_type == "spring_config" and path.lower().endswith(".properties"):
                parsed_props = self._props_parser.parse_properties(content)
            else:
                parsed_props = self._props_parser.parse_yaml(content)
            spring_conns = self._props_parser.extract_connection_info(parsed_props)
            for conn in spring_conns:
                conn["source_file"] = path
                connections.append(conn)

        elif file_type == "properties":
            parsed_props = self._props_parser.parse_properties(content)
            prop_conns = self._props_parser.extract_connection_info(parsed_props)
            for conn in prop_conns:
                conn["source_file"] = path
                connections.append(conn)

        return connections
