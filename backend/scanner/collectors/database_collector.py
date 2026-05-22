import json
import logging
import re

from scanner.collectors.base import AbstractCollector
from scanner.connectors.base import AbstractConnector

logger = logging.getLogger(__name__)

# Database detection signatures: process patterns and default ports
DB_SIGNATURES = {
    "oracle": {
        "process_patterns": ["ora_pmon", "oracle", "tnslsnr"],
        "default_port": 1521,
    },
    "postgresql": {
        "process_patterns": ["postgres", "postmaster"],
        "default_port": 5432,
    },
    "mysql": {
        "process_patterns": ["mysqld", "mariadbd", "mariadb"],
        "default_port": 3306,
    },
    "sqlserver": {
        "process_patterns": ["sqlservr", "sqlserver"],
        "default_port": 1433,
    },
    "mongodb": {
        "process_patterns": ["mongod", "mongos"],
        "default_port": 27017,
    },
}


class DatabaseCollector(AbstractCollector):
    """Detects database engines (Oracle, PostgreSQL, MySQL, SQL Server, MongoDB)."""

    SUPPORTED_OS = {"linux", "windows", "aix", "solaris"}

    def supports_os(self, os_family: str) -> bool:
        return os_family.lower() in self.SUPPORTED_OS

    async def collect(self, connector: AbstractConnector, os_family: str) -> dict:
        os_family = os_family.lower()
        if os_family == "windows":
            return await self._collect_windows(connector)
        return await self._collect_unix(connector)

    async def _collect_unix(self, connector: AbstractConnector) -> dict:
        # Get running processes
        ps_result = await connector.execute("ps -eo comm,args 2>/dev/null", timeout=15)
        process_lines = ps_result.stdout.splitlines() if ps_result.exit_code == 0 else []

        # Get listening ports
        port_result = await connector.execute(
            "ss -tlnp 2>/dev/null || netstat -tlnp 2>/dev/null", timeout=15
        )
        port_lines = port_result.stdout.splitlines() if port_result.exit_code == 0 else []

        detected_dbs: list[dict] = []

        for db_type, sig in DB_SIGNATURES.items():
            if db_type == "sqlserver":
                continue  # SQL Server is primarily Windows

            process_found = False
            port_found = False

            # Check process patterns
            for line in process_lines:
                for pattern in sig["process_patterns"]:
                    if pattern.lower() in line.lower():
                        process_found = True
                        break
                if process_found:
                    break

            # Check default port
            for line in port_lines:
                if f":{sig['default_port']}" in line:
                    port_found = True
                    break

            if process_found or port_found:
                db_info = await self._get_db_details_unix(connector, db_type)
                detected_dbs.append(db_info)

        if not detected_dbs:
            return {"databases": []}

        primary = detected_dbs[0]
        return {
            "db_engine": primary.get("engine", ""),
            "db_version": primary.get("version", ""),
            "databases": detected_dbs,
        }

    async def _collect_windows(self, connector: AbstractConnector) -> dict:
        detected_dbs: list[dict] = []

        # Check for SQL Server
        sql_check = await connector.execute(
            "Get-Service -Name 'MSSQLSERVER','MSSQL$*' -ErrorAction SilentlyContinue | "
            "Where-Object { $_.Status -eq 'Running' } | "
            "Select-Object Name, DisplayName | ConvertTo-Json -Compress",
            timeout=10,
        )
        if sql_check.exit_code == 0 and sql_check.stdout.strip():
            try:
                services = json.loads(sql_check.stdout)
                if isinstance(services, dict):
                    services = [services]
                if services:
                    version_cmd = (
                        "Invoke-Sqlcmd -Query 'SELECT @@VERSION' -ErrorAction SilentlyContinue | "
                        "Select-Object -ExpandProperty Column1"
                    )
                    ver_result = await connector.execute(version_cmd, timeout=10)
                    version = ver_result.stdout.strip() if ver_result.exit_code == 0 else ""
                    detected_dbs.append({
                        "engine": "sqlserver",
                        "version": version,
                        "instances": [s.get("Name", "") for s in services],
                    })
            except json.JSONDecodeError:
                pass

        # Check for other databases via running processes
        proc_cmd = (
            "Get-Process | Select-Object ProcessName | ConvertTo-Json -Compress"
        )
        proc_result = await connector.execute(proc_cmd, timeout=10)
        if proc_result.exit_code == 0 and proc_result.stdout.strip():
            try:
                processes = json.loads(proc_result.stdout)
                if isinstance(processes, dict):
                    processes = [processes]
                proc_names = [p.get("ProcessName", "").lower() for p in processes]

                for db_type, sig in DB_SIGNATURES.items():
                    if db_type == "sqlserver":
                        continue  # already checked
                    for pattern in sig["process_patterns"]:
                        if any(pattern.lower() in pn for pn in proc_names):
                            detected_dbs.append({
                                "engine": db_type,
                                "version": "",
                                "instances": [],
                            })
                            break
            except json.JSONDecodeError:
                pass

        if not detected_dbs:
            return {"databases": []}

        primary = detected_dbs[0]
        return {
            "db_engine": primary.get("engine", ""),
            "db_version": primary.get("version", ""),
            "databases": detected_dbs,
        }

    async def _get_db_details_unix(
        self, connector: AbstractConnector, db_type: str
    ) -> dict:
        """Extract version and instance information for a detected database."""
        info: dict = {"engine": db_type, "version": "", "instances": []}

        if db_type == "oracle":
            # Get Oracle instances from pmon processes
            pmon = await connector.execute(
                "ps -eo args | grep ora_pmon | grep -v grep", timeout=10
            )
            if pmon.exit_code == 0:
                for line in pmon.stdout.splitlines():
                    match = re.search(r"ora_pmon_(\S+)", line)
                    if match:
                        info["instances"].append(match.group(1))

            # Try to get version
            ver = await connector.execute(
                "su - oracle -c \"sqlplus -version\" 2>/dev/null | head -3", timeout=10
            )
            if ver.exit_code == 0:
                for line in ver.stdout.splitlines():
                    if "Release" in line or "Version" in line:
                        info["version"] = line.strip()
                        break

        elif db_type == "postgresql":
            ver = await connector.execute("postgres --version 2>/dev/null", timeout=10)
            if ver.exit_code == 0:
                info["version"] = ver.stdout.strip()

            # Get databases
            db_list = await connector.execute(
                "su - postgres -c \"psql -l -t\" 2>/dev/null | awk -F'|' '{print $1}'",
                timeout=10,
            )
            if db_list.exit_code == 0:
                info["instances"] = [
                    db.strip() for db in db_list.stdout.splitlines()
                    if db.strip() and db.strip() not in ("template0", "template1")
                ]

        elif db_type == "mysql":
            ver = await connector.execute("mysqld --version 2>/dev/null", timeout=10)
            if ver.exit_code == 0:
                info["version"] = ver.stdout.strip()

        elif db_type == "mongodb":
            ver = await connector.execute("mongod --version 2>/dev/null", timeout=10)
            if ver.exit_code == 0:
                for line in ver.stdout.splitlines():
                    if "db version" in line.lower():
                        info["version"] = line.strip()
                        break

        return info
