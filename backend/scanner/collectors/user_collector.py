import json
import logging

from scanner.collectors.base import AbstractCollector
from scanner.connectors.base import AbstractConnector

logger = logging.getLogger(__name__)


class UserCollector(AbstractCollector):
    """Collects local user accounts and active sessions."""

    SUPPORTED_OS = {"linux", "windows", "aix", "solaris"}

    def supports_os(self, os_family: str) -> bool:
        return os_family.lower() in self.SUPPORTED_OS

    async def collect(self, connector: AbstractConnector, os_family: str) -> dict:
        os_family = os_family.lower()
        if os_family == "windows":
            return await self._collect_windows(connector)
        return await self._collect_unix(connector)

    async def _collect_unix(self, connector: AbstractConnector) -> dict:
        local_users: list[dict] = []
        active_sessions: list[dict] = []

        # Read /etc/passwd for local users
        passwd_result = await connector.execute("cat /etc/passwd", timeout=10)
        if passwd_result.exit_code == 0:
            for line in passwd_result.stdout.splitlines():
                parts = line.strip().split(":")
                if len(parts) >= 7:
                    uid = int(parts[2]) if parts[2].isdigit() else -1
                    local_users.append({
                        "username": parts[0],
                        "uid": uid,
                        "gid": int(parts[3]) if parts[3].isdigit() else -1,
                        "home": parts[5],
                        "shell": parts[6],
                        "is_system": uid < 1000 and uid != 0,
                    })

        # Check active sessions with who
        who_result = await connector.execute("who 2>/dev/null", timeout=10)
        if who_result.exit_code == 0:
            for line in who_result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 3:
                    active_sessions.append({
                        "username": parts[0],
                        "terminal": parts[1],
                        "login_time": " ".join(parts[2:4]) if len(parts) >= 4 else parts[2],
                        "remote_host": parts[4].strip("()") if len(parts) > 4 else "",
                    })

        # Also check last logins
        last_result = await connector.execute("last -n 10 2>/dev/null", timeout=10)
        recent_logins: list[dict] = []
        if last_result.exit_code == 0:
            for line in last_result.stdout.splitlines():
                if not line.strip() or line.startswith("wtmp") or line.startswith("reboot"):
                    continue
                parts = line.split()
                if len(parts) >= 4:
                    recent_logins.append({
                        "username": parts[0],
                        "terminal": parts[1],
                        "source": parts[2] if len(parts) > 6 else "",
                    })

        return {
            "local_users": local_users,
            "active_sessions": active_sessions,
            "recent_logins": recent_logins,
        }

    async def _collect_windows(self, connector: AbstractConnector) -> dict:
        local_users: list[dict] = []
        active_sessions: list[dict] = []

        # Get local users
        user_cmd = (
            "Get-LocalUser | Select-Object Name, Enabled, LastLogon, "
            "Description | ConvertTo-Json -Compress"
        )
        user_result = await connector.execute(user_cmd, timeout=10)
        if user_result.exit_code == 0 and user_result.stdout.strip():
            try:
                parsed = json.loads(user_result.stdout)
                if isinstance(parsed, dict):
                    parsed = [parsed]
                for user in parsed:
                    local_users.append({
                        "username": user.get("Name", ""),
                        "enabled": user.get("Enabled", False),
                        "last_logon": str(user.get("LastLogon", "")),
                        "description": user.get("Description", ""),
                    })
            except json.JSONDecodeError:
                logger.warning("Failed to parse Windows user data")

        # Get active sessions via query user
        session_result = await connector.execute("query user 2>$null", timeout=10)
        if session_result.exit_code == 0:
            for line in session_result.stdout.splitlines()[1:]:  # skip header
                parts = line.split()
                if len(parts) >= 3:
                    active_sessions.append({
                        "username": parts[0].lstrip(">"),
                        "session": parts[1] if len(parts) > 3 else "",
                        "state": parts[3] if len(parts) > 3 else parts[2],
                    })

        return {
            "local_users": local_users,
            "active_sessions": active_sessions,
        }
