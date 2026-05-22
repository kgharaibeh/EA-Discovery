import logging
import re
from typing import Optional

from scanner.connectors.base import AbstractConnector

logger = logging.getLogger(__name__)


class WarInspector:
    """Inspects WAR/JAR/EAR archive files on remote systems."""

    async def inspect(self, connector: AbstractConnector, war_path: str) -> dict:
        """Inspect an archive file and return metadata.

        Uses jar -tf or unzip -l via the connector to list contents,
        and attempts to read the MANIFEST.MF file.

        Args:
            connector: An active AbstractConnector instance.
            war_path: Absolute path to the WAR/JAR/EAR file.

        Returns:
            Dict with name, size, file list, and manifest information.
        """
        name = war_path.rsplit("/", 1)[-1].rsplit("\\", 1)[-1]
        result: dict = {
            "name": name,
            "path": war_path,
            "size": 0,
            "files": [],
            "manifest": {},
            "type": self._detect_type(name),
        }

        # Get file size
        size_result = await connector.execute(
            f"stat -c %s {war_path!r} 2>/dev/null || "
            f"wc -c < {war_path!r} 2>/dev/null",
            timeout=10,
        )
        if size_result.exit_code == 0:
            size_str = size_result.stdout.strip()
            if size_str.isdigit():
                result["size"] = int(size_str)

        # List archive contents
        file_list = await self._list_contents(connector, war_path)
        result["files"] = file_list

        # Read manifest
        manifest = await self._read_manifest(connector, war_path)
        if manifest:
            result["manifest"] = manifest

        # Detect notable files
        result["has_web_xml"] = any("WEB-INF/web.xml" in f for f in file_list)
        result["has_spring_config"] = any(
            "application.properties" in f or "application.yml" in f
            for f in file_list
        )
        result["lib_count"] = sum(
            1 for f in file_list if f.startswith("WEB-INF/lib/") and f.endswith(".jar")
        )

        return result

    async def _list_contents(
        self, connector: AbstractConnector, archive_path: str
    ) -> list[str]:
        """List the contents of an archive file."""
        # Try jar first
        jar_result = await connector.execute(
            f"jar -tf {archive_path!r} 2>/dev/null", timeout=15
        )
        if jar_result.exit_code == 0 and jar_result.stdout.strip():
            return [
                line.strip()
                for line in jar_result.stdout.splitlines()
                if line.strip()
            ]

        # Fall back to unzip
        unzip_result = await connector.execute(
            f"unzip -l {archive_path!r} 2>/dev/null", timeout=15
        )
        if unzip_result.exit_code == 0:
            files: list[str] = []
            for line in unzip_result.stdout.splitlines():
                # unzip -l output format: Length Date Time Name
                match = re.match(r"\s*\d+\s+\d{2}-\d{2}-\d{2,4}\s+\d{2}:\d{2}\s+(.+)", line)
                if match:
                    files.append(match.group(1).strip())
            return files

        return []

    async def _read_manifest(
        self, connector: AbstractConnector, archive_path: str
    ) -> dict[str, str]:
        """Extract and parse MANIFEST.MF from the archive."""
        # Try using unzip to extract just the manifest
        manifest_result = await connector.execute(
            f"unzip -p {archive_path!r} META-INF/MANIFEST.MF 2>/dev/null",
            timeout=10,
        )
        if manifest_result.exit_code != 0 or not manifest_result.stdout.strip():
            # Try jar
            manifest_result = await connector.execute(
                f"jar -xf {archive_path!r} META-INF/MANIFEST.MF 2>/dev/null && "
                "cat META-INF/MANIFEST.MF && rm -rf META-INF",
                timeout=10,
            )

        if manifest_result.exit_code != 0 or not manifest_result.stdout.strip():
            return {}

        return self._parse_manifest(manifest_result.stdout)

    def _parse_manifest(self, content: str) -> dict[str, str]:
        """Parse MANIFEST.MF content into a dict."""
        manifest: dict[str, str] = {}
        current_key = ""
        current_value = ""

        for line in content.splitlines():
            if line.startswith(" ") and current_key:
                # Continuation line
                current_value += line[1:]
            else:
                # Save previous entry
                if current_key:
                    manifest[current_key] = current_value
                # Parse new entry
                if ":" in line:
                    current_key, _, current_value = line.partition(":")
                    current_key = current_key.strip()
                    current_value = current_value.strip()
                else:
                    current_key = ""
                    current_value = ""

        if current_key:
            manifest[current_key] = current_value

        return manifest

    @staticmethod
    def _detect_type(filename: str) -> str:
        """Detect archive type from filename extension."""
        lower = filename.lower()
        if lower.endswith(".war"):
            return "WAR"
        elif lower.endswith(".ear"):
            return "EAR"
        elif lower.endswith(".jar"):
            return "JAR"
        return "UNKNOWN"
