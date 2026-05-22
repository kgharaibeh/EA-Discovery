import logging
import re
from typing import Optional
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

# JDBC URL patterns for various databases
JDBC_PATTERNS = {
    "oracle_thin": re.compile(
        r"jdbc:oracle:thin:(?:@//|@)(?P<host>[^:/]+):(?P<port>\d+)[:/](?P<database>\S+)"
    ),
    "oracle_sid": re.compile(
        r"jdbc:oracle:thin:@(?P<host>[^:]+):(?P<port>\d+):(?P<database>\S+)"
    ),
    "postgresql": re.compile(
        r"jdbc:postgresql://(?P<host>[^:/]+)(?::(?P<port>\d+))?/(?P<database>[^?\s]+)"
    ),
    "mysql": re.compile(
        r"jdbc:mysql://(?P<host>[^:/]+)(?::(?P<port>\d+))?/(?P<database>[^?\s]+)"
    ),
    "sqlserver": re.compile(
        r"jdbc:sqlserver://(?P<host>[^:;]+)(?::(?P<port>\d+))?(?:;.*?databaseName=(?P<database>[^;\s]+))?"
    ),
    "db2": re.compile(
        r"jdbc:db2://(?P<host>[^:/]+)(?::(?P<port>\d+))?/(?P<database>[^:\s]+)"
    ),
}

# Default ports per database type
DEFAULT_PORTS = {
    "oracle": 1521,
    "postgresql": 5432,
    "mysql": 3306,
    "sqlserver": 1433,
    "db2": 50000,
    "mongodb": 27017,
}


class ConnectionStringParser:
    """Parses JDBC, ODBC, and Spring datasource connection strings."""

    def parse_jdbc(self, jdbc_url: str) -> Optional[dict]:
        """Parse a JDBC URL into connection components.

        Args:
            jdbc_url: A JDBC connection string, e.g.
                      jdbc:oracle:thin:@host:1521/SID

        Returns:
            Dict with host, port, database, protocol keys, or None if unparseable.
        """
        jdbc_url = jdbc_url.strip().rstrip(";,\"' ")

        for db_type, pattern in JDBC_PATTERNS.items():
            match = pattern.search(jdbc_url)
            if match:
                groups = match.groupdict()
                protocol = db_type.split("_")[0]  # e.g. "oracle_thin" -> "oracle"
                port_str = groups.get("port")
                port = int(port_str) if port_str else DEFAULT_PORTS.get(protocol, 0)

                return {
                    "target_host": groups.get("host", ""),
                    "target_port": port,
                    "database": groups.get("database", ""),
                    "protocol": protocol,
                    "connection_string": jdbc_url,
                }

        logger.debug("Could not parse JDBC URL: %s", jdbc_url)
        return None

    def parse_odbc(self, odbc_string: str) -> Optional[dict]:
        """Parse an ODBC connection string into connection components.

        Args:
            odbc_string: An ODBC connection string, e.g.
                         Server=host;Database=mydb;...

        Returns:
            Dict with host, port, database, protocol keys, or None if unparseable.
        """
        odbc_string = odbc_string.strip()
        params: dict[str, str] = {}

        for part in odbc_string.split(";"):
            part = part.strip()
            if "=" in part:
                key, _, value = part.partition("=")
                params[key.strip().lower()] = value.strip()

        host = (
            params.get("server")
            or params.get("data source")
            or params.get("host")
            or ""
        )
        if not host:
            return None

        # Handle host\instance or host,port format (SQL Server)
        port = 0
        if "," in host:
            host, port_str = host.rsplit(",", 1)
            port = int(port_str) if port_str.isdigit() else 0
        elif "\\" in host:
            host = host.split("\\")[0]

        database = params.get("database") or params.get("initial catalog") or ""

        # Detect protocol from driver or keywords
        protocol = "unknown"
        driver = params.get("driver", "").lower()
        if "oracle" in driver:
            protocol = "oracle"
            port = port or DEFAULT_PORTS["oracle"]
        elif "sql server" in driver or "sqlserver" in driver:
            protocol = "sqlserver"
            port = port or DEFAULT_PORTS["sqlserver"]
        elif "mysql" in driver:
            protocol = "mysql"
            port = port or DEFAULT_PORTS["mysql"]
        elif "postgres" in driver or "pgsql" in driver:
            protocol = "postgresql"
            port = port or DEFAULT_PORTS["postgresql"]

        return {
            "target_host": host,
            "target_port": port,
            "database": database,
            "protocol": protocol,
            "connection_string": odbc_string,
        }

    def parse_spring_datasource(self, props: dict) -> Optional[dict]:
        """Parse Spring datasource properties into connection components.

        Args:
            props: Dict of Spring properties, typically containing keys like
                   spring.datasource.url, spring.datasource.username, etc.

        Returns:
            Dict with connection details, or None if no datasource URL found.
        """
        url = (
            props.get("spring.datasource.url")
            or props.get("spring.datasource.jdbc-url")
            or ""
        )

        if not url:
            # Check for R2DBC (reactive)
            url = props.get("spring.r2dbc.url", "")

        if url.startswith("jdbc:"):
            result = self.parse_jdbc(url)
            if result:
                # Enrich with username if available
                username = props.get("spring.datasource.username", "")
                if username:
                    result["username"] = username
                return result

        return None
