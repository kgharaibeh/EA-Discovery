import logging
import re
from typing import Any, Optional

from scanner.parsers.connection_string import ConnectionStringParser

logger = logging.getLogger(__name__)


class PropertiesParser:
    """Parses Java .properties and YAML configuration files."""

    def __init__(self) -> None:
        self._conn_parser = ConnectionStringParser()

    def parse_properties(self, content: str) -> dict[str, str]:
        """Parse a Java .properties file into a dict of key-value pairs.

        Handles comments (#, !), continuation lines (trailing backslash),
        and both = and : delimiters.

        Args:
            content: Raw content of a .properties file.

        Returns:
            Dict mapping property keys to their string values.
        """
        result: dict[str, str] = {}
        current_line = ""

        for line in content.splitlines():
            stripped = line.strip()

            # Skip comments and empty lines
            if not stripped or stripped.startswith("#") or stripped.startswith("!"):
                continue

            # Handle line continuation
            if stripped.endswith("\\"):
                current_line += stripped[:-1]
                continue
            else:
                current_line += stripped

            # Split on first = or :
            match = re.match(r"^([^=:]+)[=:](.*)", current_line)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()
                result[key] = value

            current_line = ""

        return result

    def parse_yaml(self, content: str) -> dict[str, Any]:
        """Parse a YAML file into a flattened dict with dotted keys.

        Uses a simple parser for common Spring configuration patterns.
        Falls back to a basic line-by-line parser if PyYAML is not available.

        Args:
            content: Raw YAML content.

        Returns:
            Flattened dict with dotted key paths (e.g. "spring.datasource.url").
        """
        try:
            import yaml

            raw = yaml.safe_load(content)
            if isinstance(raw, dict):
                return self._flatten_dict(raw)
            return {}
        except ImportError:
            logger.debug("PyYAML not available, using basic YAML parser")
            return self._basic_yaml_parse(content)
        except Exception as exc:
            logger.debug("YAML parse error: %s", exc)
            return self._basic_yaml_parse(content)

    def extract_connection_info(self, parsed: dict[str, Any]) -> list[dict]:
        """Extract connection targets from parsed properties or YAML.

        Looks for Spring datasource URLs, custom connection properties,
        and other common patterns.

        Args:
            parsed: Flattened dict of configuration properties.

        Returns:
            List of connection target dicts.
        """
        connections: list[dict] = []

        # Check for Spring datasource
        spring_result = self._conn_parser.parse_spring_datasource(parsed)
        if spring_result:
            connections.append(spring_result)

        # Look for any property containing JDBC URLs
        for key, value in parsed.items():
            if not isinstance(value, str):
                continue
            value_str = str(value)

            if value_str.startswith("jdbc:") and key not in (
                "spring.datasource.url",
                "spring.datasource.jdbc-url",
            ):
                result = self._conn_parser.parse_jdbc(value_str)
                if result:
                    result["property_key"] = key
                    connections.append(result)

            # Look for host:port patterns in connection-related keys
            if any(
                kw in key.lower()
                for kw in ("host", "server", "endpoint", "url", "address")
            ):
                host_port = re.match(r"^([a-zA-Z0-9._-]+):(\d+)$", value_str)
                if host_port:
                    connections.append({
                        "target_host": host_port.group(1),
                        "target_port": int(host_port.group(2)),
                        "property_key": key,
                        "protocol": "unknown",
                    })

        return connections

    def _flatten_dict(
        self, data: dict, prefix: str = "", sep: str = "."
    ) -> dict[str, Any]:
        """Flatten a nested dict using dotted key paths."""
        items: dict[str, Any] = {}
        for key, value in data.items():
            new_key = f"{prefix}{sep}{key}" if prefix else str(key)
            if isinstance(value, dict):
                items.update(self._flatten_dict(value, new_key, sep))
            elif isinstance(value, list):
                items[new_key] = value
            else:
                items[new_key] = value
        return items

    def _basic_yaml_parse(self, content: str) -> dict[str, str]:
        """Simple line-by-line YAML parser for key: value pairs.

        Handles indented blocks by building dotted key paths.
        """
        result: dict[str, str] = {}
        indent_stack: list[tuple[int, str]] = []

        for line in content.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue

            indent = len(line) - len(line.lstrip())

            # Pop stack entries with >= current indent
            while indent_stack and indent_stack[-1][0] >= indent:
                indent_stack.pop()

            match = re.match(r"^(\S[^:]*):(.*)$", stripped)
            if match:
                key = match.group(1).strip()
                value = match.group(2).strip()

                if indent_stack:
                    prefix = ".".join(k for _, k in indent_stack)
                    full_key = f"{prefix}.{key}"
                else:
                    full_key = key

                if value and not value.startswith("#"):
                    # Strip quotes
                    value = value.strip("'\"")
                    result[full_key] = value
                else:
                    # This key has sub-keys
                    indent_stack.append((indent, key))

        return result
