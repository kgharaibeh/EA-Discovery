import asyncio
import json
import logging
import time
from typing import Optional

import winrm

from scanner.connectors.base import AbstractConnector, CommandResult

logger = logging.getLogger(__name__)


class WinRMConnector(AbstractConnector):
    """WinRM connector using pywinrm wrapped in asyncio.to_thread for async compatibility."""

    def __init__(self) -> None:
        self._session: Optional[winrm.Session] = None
        self._host: str = ""
        self._port: int = 5985
        self._connected: bool = False

    async def connect(self, host: str, port: int, credentials: dict) -> None:
        """Establish a WinRM session to the target host.

        Args:
            host: Target hostname or IP address.
            port: WinRM port (5985 for HTTP, 5986 for HTTPS).
            credentials: Dict with 'username' and 'password' keys.
                         Optional 'transport' key (default: 'ntlm').
        """
        self._host = host
        self._port = port

        username = credentials.get("username", "Administrator")
        password = credentials.get("password", "")
        transport = credentials.get("transport", "ntlm")
        scheme = "https" if port == 5986 else "http"
        endpoint = f"{scheme}://{host}:{port}/wsman"

        try:
            self._session = winrm.Session(
                endpoint,
                auth=(username, password),
                transport=transport,
                server_cert_validation="ignore",
            )
            # Validate connectivity with a lightweight command
            await asyncio.to_thread(self._session.run_ps, "echo ok")
            self._connected = True
            logger.info("WinRM connected to %s:%d", host, port)
        except Exception as exc:
            self._connected = False
            logger.error("WinRM connection failed to %s:%d: %s", host, port, exc)
            raise ConnectionError(f"WinRM connection to {host}:{port} failed: {exc}") from exc

    async def execute(self, command: str, timeout: int = 30) -> CommandResult:
        """Execute a PowerShell command on the remote host."""
        if not self._session or not self._connected:
            raise RuntimeError("Not connected. Call connect() first.")

        start = time.monotonic()
        try:
            result = await asyncio.wait_for(
                asyncio.to_thread(self._session.run_ps, command),
                timeout=timeout,
            )
            duration_ms = (time.monotonic() - start) * 1000
            return CommandResult(
                stdout=result.std_out.decode("utf-8", errors="replace") if result.std_out else "",
                stderr=result.std_err.decode("utf-8", errors="replace") if result.std_err else "",
                exit_code=result.status_code,
                duration_ms=round(duration_ms, 2),
            )
        except asyncio.TimeoutError:
            duration_ms = (time.monotonic() - start) * 1000
            logger.warning("Command timed out on %s after %ds", self._host, timeout)
            return CommandResult(
                stdout="",
                stderr=f"Command timed out after {timeout}s",
                exit_code=-1,
                duration_ms=round(duration_ms, 2),
            )
        except Exception as exc:
            duration_ms = (time.monotonic() - start) * 1000
            logger.error("Command execution failed on %s: %s", self._host, exc)
            return CommandResult(
                stdout="",
                stderr=str(exc),
                exit_code=-1,
                duration_ms=round(duration_ms, 2),
            )

    async def read_file(self, path: str, max_bytes: int = 1_048_576) -> str:
        """Read a file from the remote Windows host using Get-Content."""
        ps_command = (
            f"Get-Content -Path '{path}' -Encoding UTF8 -TotalCount "
            f"([math]::Ceiling({max_bytes} / 80)) -ErrorAction Stop"
        )
        result = await self.execute(ps_command, timeout=15)
        if result.exit_code != 0:
            raise FileNotFoundError(f"Cannot read {path} on {self._host}: {result.stderr}")
        return result.stdout

    async def list_directory(self, path: str) -> list[dict]:
        """List directory contents using Get-ChildItem and return parsed JSON."""
        ps_command = (
            f"Get-ChildItem -Path '{path}' -Force | "
            "Select-Object Name, Length, LastWriteTime, "
            "@{Name='IsDirectory';Expression={$_.PSIsContainer}} | "
            "ConvertTo-Json -Compress"
        )
        result = await self.execute(ps_command, timeout=15)
        if result.exit_code != 0:
            raise FileNotFoundError(f"Cannot list {path} on {self._host}: {result.stderr}")

        if not result.stdout.strip():
            return []

        try:
            parsed = json.loads(result.stdout)
            # ConvertTo-Json returns a single object when there's only one item
            if isinstance(parsed, dict):
                parsed = [parsed]
            return parsed
        except json.JSONDecodeError:
            logger.warning("Failed to parse directory listing JSON from %s", self._host)
            return []

    async def disconnect(self) -> None:
        """Close the WinRM session."""
        self._session = None
        self._connected = False
        logger.info("WinRM disconnected from %s:%d", self._host, self._port)

    def is_connected(self) -> bool:
        """Check whether the WinRM session is active."""
        return self._connected and self._session is not None
