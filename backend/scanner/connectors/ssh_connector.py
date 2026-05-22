import time
import logging
from typing import Optional

import asyncssh

from scanner.connectors.base import AbstractConnector, CommandResult

logger = logging.getLogger(__name__)


class SSHConnector(AbstractConnector):
    """SSH connector using asyncssh for async remote command execution."""

    def __init__(self) -> None:
        self._conn: Optional[asyncssh.SSHClientConnection] = None
        self._host: str = ""
        self._port: int = 22

    async def connect(self, host: str, port: int, credentials: dict) -> None:
        """Connect to a remote host via SSH.

        Args:
            host: Target hostname or IP address.
            port: SSH port number.
            credentials: Dict with keys such as 'username', 'password',
                         'private_key' (PEM string), and 'passphrase'.
        """
        self._host = host
        self._port = port

        connect_kwargs: dict = {
            "host": host,
            "port": port,
            "username": credentials.get("username", "root"),
            "known_hosts": None,  # disable host key checking for scanning
        }

        private_key = credentials.get("private_key")
        passphrase = credentials.get("passphrase")
        password = credentials.get("password")

        if private_key:
            key = asyncssh.import_private_key(private_key, passphrase)
            connect_kwargs["client_keys"] = [key]
        elif password:
            connect_kwargs["password"] = password

        try:
            self._conn = await asyncssh.connect(**connect_kwargs)
            logger.info("SSH connected to %s:%d", host, port)
        except (asyncssh.Error, OSError) as exc:
            logger.error("SSH connection failed to %s:%d: %s", host, port, exc)
            raise ConnectionError(f"SSH connection to {host}:{port} failed: {exc}") from exc

    async def execute(self, command: str, timeout: int = 30) -> CommandResult:
        """Execute a command on the remote host and return the result."""
        if not self._conn:
            raise RuntimeError("Not connected. Call connect() first.")

        start = time.monotonic()
        try:
            result = await asyncssh.wait_for(
                self._conn.run(command, check=False),
                timeout=timeout,
            )
            duration_ms = (time.monotonic() - start) * 1000
            return CommandResult(
                stdout=result.stdout or "",
                stderr=result.stderr or "",
                exit_code=result.exit_status or 0,
                duration_ms=round(duration_ms, 2),
            )
        except asyncssh.TimeoutError as exc:
            duration_ms = (time.monotonic() - start) * 1000
            logger.warning("Command timed out on %s after %ds: %s", self._host, timeout, command)
            return CommandResult(
                stdout="",
                stderr=f"Command timed out after {timeout}s",
                exit_code=-1,
                duration_ms=round(duration_ms, 2),
            )
        except asyncssh.Error as exc:
            duration_ms = (time.monotonic() - start) * 1000
            logger.error("Command execution failed on %s: %s", self._host, exc)
            return CommandResult(
                stdout="",
                stderr=str(exc),
                exit_code=-1,
                duration_ms=round(duration_ms, 2),
            )

    async def read_file(self, path: str, max_bytes: int = 1_048_576) -> str:
        """Read a file from the remote host using cat with byte limit."""
        result = await self.execute(f"head -c {max_bytes} {path!r}", timeout=15)
        if result.exit_code != 0:
            raise FileNotFoundError(f"Cannot read {path} on {self._host}: {result.stderr}")
        return result.stdout

    async def list_directory(self, path: str) -> list[dict]:
        """List directory contents using ls -la and parse the output."""
        result = await self.execute(f"ls -la {path!r}", timeout=15)
        if result.exit_code != 0:
            raise FileNotFoundError(f"Cannot list {path} on {self._host}: {result.stderr}")

        entries: list[dict] = []
        for line in result.stdout.strip().splitlines()[1:]:  # skip "total" line
            parts = line.split(None, 8)
            if len(parts) < 9:
                continue
            entries.append({
                "permissions": parts[0],
                "links": parts[1],
                "owner": parts[2],
                "group": parts[3],
                "size": int(parts[4]) if parts[4].isdigit() else 0,
                "month": parts[5],
                "day": parts[6],
                "time_or_year": parts[7],
                "name": parts[8],
                "is_directory": parts[0].startswith("d"),
            })
        return entries

    async def disconnect(self) -> None:
        """Close the SSH connection."""
        if self._conn:
            self._conn.close()
            await self._conn.wait_closed()
            self._conn = None
            logger.info("SSH disconnected from %s:%d", self._host, self._port)

    def is_connected(self) -> bool:
        """Check whether the SSH connection is active."""
        return self._conn is not None and not self._conn.is_closed()
