import logging
import re
from typing import Optional
from xml.etree import ElementTree

from scanner.parsers.connection_string import ConnectionStringParser

logger = logging.getLogger(__name__)


class XmlConfigParser:
    """Parses Java EE and application server XML configuration files."""

    def __init__(self) -> None:
        self._conn_parser = ConnectionStringParser()

    def parse_web_xml(self, content: str) -> list[dict]:
        """Parse a web.xml file for resource references.

        Extracts <resource-ref> elements that define database connections,
        JMS queues, and other JNDI resources.

        Args:
            content: Raw XML content of web.xml.

        Returns:
            List of resource reference dicts.
        """
        results: list[dict] = []
        try:
            # Strip namespace for easier parsing
            content = re.sub(r'\sxmlns="[^"]*"', "", content, count=1)
            root = ElementTree.fromstring(content)
        except ElementTree.ParseError as exc:
            logger.debug("Failed to parse web.xml: %s", exc)
            return results

        for ref in root.iter("resource-ref"):
            res_name = self._get_text(ref, "res-ref-name")
            res_type = self._get_text(ref, "res-type")
            description = self._get_text(ref, "description")

            if res_name:
                entry: dict = {
                    "resource_name": res_name,
                    "resource_type": res_type,
                    "description": description,
                    "type": "resource_ref",
                }
                # Try to determine target from naming convention
                if "javax.sql.DataSource" in (res_type or ""):
                    entry["is_datasource"] = True
                results.append(entry)

        # Also check for <env-entry> elements
        for entry_el in root.iter("env-entry"):
            name = self._get_text(entry_el, "env-entry-name")
            value = self._get_text(entry_el, "env-entry-value")
            if name and value:
                results.append({
                    "resource_name": name,
                    "value": value,
                    "type": "env_entry",
                })

        return results

    def parse_server_xml(self, content: str) -> list[dict]:
        """Parse a Tomcat server.xml for datasource definitions.

        Extracts <Resource> elements from GlobalNamingResources and Context.

        Args:
            content: Raw XML content of server.xml.

        Returns:
            List of datasource configuration dicts.
        """
        results: list[dict] = []
        try:
            root = ElementTree.fromstring(content)
        except ElementTree.ParseError as exc:
            logger.debug("Failed to parse server.xml: %s", exc)
            return results

        # Find all Resource elements (datasources)
        for resource in root.iter("Resource"):
            attribs = resource.attrib
            res_type = attribs.get("type", "")

            if "DataSource" not in res_type:
                continue

            url = attribs.get("url", "")
            entry: dict = {
                "name": attribs.get("name", ""),
                "type": "datasource",
                "driver": attribs.get("driverClassName", ""),
                "url": url,
                "username": attribs.get("username", ""),
                "max_connections": attribs.get("maxTotal", attribs.get("maxActive", "")),
            }

            # Parse the JDBC URL for connection details
            if url.startswith("jdbc:"):
                parsed = self._conn_parser.parse_jdbc(url)
                if parsed:
                    entry["target_host"] = parsed["target_host"]
                    entry["target_port"] = parsed["target_port"]
                    entry["database"] = parsed["database"]
                    entry["protocol"] = parsed["protocol"]

            results.append(entry)

        return results

    def parse_weblogic_config(self, content: str) -> list[dict]:
        """Parse WebLogic configuration XML for JNDI datasource definitions.

        Handles both config.xml and jdbc-data-source XML formats.

        Args:
            content: Raw XML content of the WebLogic config file.

        Returns:
            List of JNDI datasource configuration dicts.
        """
        results: list[dict] = []
        try:
            # Strip namespaces for easier parsing
            content = re.sub(r'\sxmlns(?::\w+)?="[^"]*"', "", content)
            root = ElementTree.fromstring(content)
        except ElementTree.ParseError as exc:
            logger.debug("Failed to parse WebLogic config: %s", exc)
            return results

        # Look for jdbc-data-source elements
        for ds in root.iter("jdbc-data-source"):
            name = self._get_text(ds, "name")
            jndi = self._get_text(ds, "jndi-name")

            # Look for connection pool params
            url = ""
            driver = ""
            for pool in ds.iter("jdbc-driver-params"):
                url = self._get_text(pool, "url") or ""
                driver = self._get_text(pool, "driver-name") or ""

            entry: dict = {
                "name": name or "",
                "jndi_name": jndi or "",
                "type": "jndi_datasource",
                "driver": driver,
                "url": url,
            }

            if url.startswith("jdbc:"):
                parsed = self._conn_parser.parse_jdbc(url)
                if parsed:
                    entry["target_host"] = parsed["target_host"]
                    entry["target_port"] = parsed["target_port"]
                    entry["database"] = parsed["database"]
                    entry["protocol"] = parsed["protocol"]

            results.append(entry)

        # Also look for generic data-source elements in config.xml
        for ds in root.iter("data-source"):
            name = self._get_text(ds, "name")
            jndi = self._get_text(ds, "jndi-name")
            if name:
                results.append({
                    "name": name,
                    "jndi_name": jndi or "",
                    "type": "jndi_datasource",
                })

        return results

    @staticmethod
    def _get_text(element: ElementTree.Element, tag: str) -> Optional[str]:
        """Get text content of a child element, or None."""
        child = element.find(tag)
        if child is not None and child.text:
            return child.text.strip()
        return None
