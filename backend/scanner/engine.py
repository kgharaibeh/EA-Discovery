import asyncio
import time
from datetime import datetime
from typing import Any

import structlog

from app.config import settings
from app.repositories.asset_repo import AssetRepository
from app.repositories.relationship_repo import RelationshipRepository
from credentials.manager import CredentialManager
from scanner.connectors.base import AbstractConnector
from scanner.connectors.ssh_connector import SSHConnector
from scanner.connectors.winrm_connector import WinRMConnector
from scanner.collectors.os_collector import OSCollector
from scanner.collectors.port_collector import PortCollector
from scanner.collectors.service_collector import ServiceCollector
from scanner.collectors.network_collector import NetworkCollector
from scanner.collectors.software_collector import SoftwareCollector
from scanner.collectors.appserver_collector import AppServerCollector
from scanner.collectors.database_collector import DatabaseCollector
from scanner.collectors.config_parser import ConfigParserCollector
from scanner.collectors.filesystem_collector import FilesystemCollector
from scanner.target import ScanTarget

logger = structlog.get_logger()


class ScanEngine:
    def __init__(
        self,
        credential_manager: CredentialManager,
        asset_repo: AssetRepository,
        relationship_repo: RelationshipRepository,
    ):
        self.credential_manager = credential_manager
        self.asset_repo = asset_repo
        self.relationship_repo = relationship_repo
        self._semaphore = asyncio.Semaphore(settings.scan_concurrency)

    async def execute_scan(self, scan: dict) -> dict:
        targets = [
            ScanTarget(
                host=t["host"],
                credential_id=t.get("credential_id", ""),
            )
            for t in scan.get("targets", [])
        ]

        results = {
            "assets_discovered": 0,
            "relationships_discovered": 0,
            "new_assets": 0,
            "updated_assets": 0,
            "completed_targets": 0,
            "failed_targets": [],
        }

        scan_id = scan["_id"]
        tasks = [self._scan_target_with_semaphore(t, scan_id, results) for t in targets]
        await asyncio.gather(*tasks, return_exceptions=True)

        return results

    async def _scan_target_with_semaphore(self, target: ScanTarget, scan_id: str, results: dict):
        async with self._semaphore:
            try:
                await self._scan_single_target(target, scan_id, results)
                results["completed_targets"] += 1
            except Exception as e:
                logger.error("scan_target_failed", host=target.host, error=str(e))
                results["failed_targets"].append({"host": target.host, "error": str(e)})

    async def _scan_single_target(self, target: ScanTarget, scan_id: str, results: dict):
        connector = await self._connect(target)
        try:
            os_data = await OSCollector().collect(connector, "unknown")
            os_family = os_data.get("os_family", "unknown")
            target.os_family = os_family

            collectors_data: dict[str, Any] = {**os_data}
            collectors = [
                PortCollector(),
                ServiceCollector(),
                NetworkCollector(),
                SoftwareCollector(),
                AppServerCollector(),
                DatabaseCollector(),
                ConfigParserCollector(),
                FilesystemCollector(),
            ]

            for collector in collectors:
                if collector.supports_os(os_family):
                    try:
                        data = await collector.collect(connector, os_family)
                        collectors_data.update(data)
                    except Exception as e:
                        logger.warning("collector_failed", collector=type(collector).__name__, error=str(e))

            asset_type = self._determine_asset_type(collectors_data)
            asset_doc = {
                "hostname": collectors_data.get("hostname", target.host),
                "ip_addresses": collectors_data.get("ip_addresses", [target.host]),
                "asset_type": asset_type,
                "status": "active",
                "os_family": os_family,
                "os_version": collectors_data.get("os_version", ""),
                "discovered_at": datetime.utcnow(),
                "last_scanned": datetime.utcnow(),
                "scan_id": scan_id,
                "source": "infrastructure_scan",
                "open_ports": collectors_data.get("open_ports", []),
                "installed_software": collectors_data.get("installed_software", []),
                "running_services": collectors_data.get("running_services", []),
                "listening_services": collectors_data.get("listening_services", []),
                "app_server_type": collectors_data.get("app_server_type"),
                "deployed_artifacts": collectors_data.get("deployed_artifacts", []),
                "db_engine": collectors_data.get("db_engine"),
                "db_version": collectors_data.get("db_version"),
                "databases": collectors_data.get("databases", []),
                "config_files": collectors_data.get("config_files", []),
                "data_classifications": [],
                "business_context": None,
                "ai_suggestions": [],
                "human_verified": False,
                "tags": [],
                "custom_attributes": {},
            }

            existing = await self.asset_repo.find_by_hostname(asset_doc["hostname"])
            asset_id = await self.asset_repo.upsert_by_hostname(asset_doc["hostname"], asset_doc)
            asset_doc["_id"] = asset_id

            if existing:
                results["updated_assets"] += 1
            else:
                results["new_assets"] += 1
            results["assets_discovered"] += 1

            rel_count = await self._extract_relationships(collectors_data, asset_id, scan_id)
            results["relationships_discovered"] += rel_count

        finally:
            await connector.disconnect()

    async def _connect(self, target: ScanTarget) -> AbstractConnector:
        creds = {}
        if target.credential_id:
            creds = await self.credential_manager.get_credential(target.credential_id)

        connector: AbstractConnector
        try:
            connector = SSHConnector()
            await connector.connect(target.host, settings.ssh_default_port, creds)
            return connector
        except Exception:
            connector = WinRMConnector()
            await connector.connect(target.host, settings.winrm_default_port, creds)
            return connector

    async def _extract_relationships(self, data: dict, asset_id: str, scan_id: str) -> int:
        count = 0

        for conn in data.get("connections", []):
            remote_ip = conn.get("remote_ip", "")
            remote_port = conn.get("remote_port", 0)
            if not remote_ip or remote_ip.startswith("127.") or remote_ip == "::1":
                continue

            target_asset = await self.asset_repo.resolve_by_ip_port(remote_ip, remote_port)
            if not target_asset:
                continue

            rel_type = self._infer_relationship_type(remote_port)
            rel_doc = {
                "source_asset_id": asset_id,
                "target_asset_id": target_asset["_id"],
                "relationship_type": rel_type,
                "direction": "outbound",
                "source_method": "network_connection",
                "evidence": [{
                    "type": "active_connection",
                    "local_port": conn.get("local_port"),
                    "remote_ip": remote_ip,
                    "remote_port": remote_port,
                    "process": conn.get("process", ""),
                }],
                "confidence": 0.9,
                "protocol": conn.get("protocol", "tcp"),
                "port": remote_port,
                "endpoint": None,
                "request_count": None,
                "avg_latency_ms": None,
                "last_seen": datetime.utcnow(),
                "discovered_at": datetime.utcnow(),
                "scan_id": scan_id,
                "human_verified": False,
            }

            await self.relationship_repo.upsert_relationship(
                asset_id, target_asset["_id"], rel_type, rel_doc
            )
            count += 1

        for parsed_conn in data.get("parsed_connections", []):
            target_host = parsed_conn.get("target_host", "")
            target_port = parsed_conn.get("target_port", 0)
            if not target_host:
                continue

            target_asset = await self.asset_repo.resolve_by_ip_port(target_host, target_port)
            if not target_asset:
                continue

            rel_doc = {
                "source_asset_id": asset_id,
                "target_asset_id": target_asset["_id"],
                "relationship_type": "queries",
                "direction": "outbound",
                "source_method": "config_parse",
                "evidence": [{
                    "type": "config_file",
                    "connection_string": parsed_conn.get("connection_string", ""),
                    "file_path": parsed_conn.get("source_file", ""),
                    "protocol": parsed_conn.get("protocol", ""),
                }],
                "confidence": 0.95,
                "protocol": parsed_conn.get("protocol", ""),
                "port": target_port,
                "endpoint": None,
                "request_count": None,
                "avg_latency_ms": None,
                "last_seen": None,
                "discovered_at": datetime.utcnow(),
                "scan_id": scan_id,
                "human_verified": False,
            }

            await self.relationship_repo.upsert_relationship(
                asset_id, target_asset["_id"], "queries", rel_doc
            )
            count += 1

        return count

    @staticmethod
    def _determine_asset_type(data: dict) -> str:
        if data.get("app_server_type"):
            return "app_server"
        if data.get("db_engine"):
            return "database"
        return "server"

    @staticmethod
    def _infer_relationship_type(remote_port: int) -> str:
        db_ports = {1521, 1433, 3306, 5432, 27017, 6379, 9042}
        if remote_port in db_ports:
            return "queries"
        http_ports = {80, 443, 8080, 8443, 9090, 3000, 5000}
        if remote_port in http_ports:
            return "calls_api"
        if remote_port == 389 or remote_port == 636:
            return "authenticates_via"
        return "connects_to"
