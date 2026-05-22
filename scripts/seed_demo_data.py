"""Seed MongoDB with demo data for development and testing."""
import asyncio
from datetime import datetime, timedelta
from uuid import uuid4

from motor.motor_asyncio import AsyncIOMotorClient


async def seed():
    client = AsyncIOMotorClient("mongodb://localhost:27017/ea_discovery")
    db = client["ea_discovery"]

    await db.assets.drop()
    await db.relationships.drop()
    await db.scans.drop()
    await db.intelligence_suggestions.drop()

    scan_id = str(uuid4())
    now = datetime.utcnow()

    assets = [
        {
            "_id": "asset-weblogic-01",
            "hostname": "weblogic-prod-01",
            "ip_addresses": ["10.0.1.10"],
            "asset_type": "app_server",
            "status": "active",
            "os_family": "linux",
            "os_version": "Red Hat Enterprise Linux 8.9",
            "discovered_at": now,
            "last_scanned": now,
            "scan_id": scan_id,
            "source": "infrastructure_scan",
            "open_ports": [
                {"port": 22, "protocol": "tcp", "service": "ssh"},
                {"port": 7001, "protocol": "tcp", "service": "weblogic"},
                {"port": 7002, "protocol": "tcp", "service": "weblogic-ssl"},
                {"port": 9090, "protocol": "tcp", "service": "admin-console"},
            ],
            "installed_software": [
                {"name": "java-17-openjdk", "version": "17.0.9"},
                {"name": "oracle-weblogic", "version": "14.1.1"},
            ],
            "running_services": [
                {"name": "weblogic.Server", "pid": 12345, "user": "oracle"},
                {"name": "sshd", "pid": 1000, "user": "root"},
            ],
            "listening_services": [
                {"port": 7001, "pid": 12345, "process": "java"},
                {"port": 7002, "pid": 12345, "process": "java"},
            ],
            "app_server_type": "weblogic",
            "deployed_artifacts": [
                {"name": "pnl-webapp.war", "path": "/opt/weblogic/domains/prod/deployments/", "size": 45000000},
                {"name": "reporting-api.war", "path": "/opt/weblogic/domains/prod/deployments/", "size": 12000000},
            ],
            "db_engine": None,
            "db_version": None,
            "databases": [],
            "config_files": [
                {"path": "/opt/weblogic/domains/prod/config/config.xml", "type": "weblogic_config"},
                {"path": "/opt/weblogic/domains/prod/config/jdbc/pnl-ds.xml", "type": "datasource"},
            ],
            "data_classifications": [],
            "business_context": {
                "purpose": "Hosts the Profit & Loss web application and reporting API",
                "department": "Finance",
                "criticality": "critical",
                "application_name": "P&L Management System",
            },
            "human_verified": True,
            "tags": ["production", "finance", "critical"],
            "custom_attributes": {},
        },
        {
            "_id": "asset-oracle-01",
            "hostname": "oracle-db-prod-01",
            "ip_addresses": ["10.0.2.20"],
            "asset_type": "database",
            "status": "active",
            "os_family": "linux",
            "os_version": "Oracle Linux 8.8",
            "discovered_at": now,
            "last_scanned": now,
            "scan_id": scan_id,
            "source": "infrastructure_scan",
            "open_ports": [
                {"port": 22, "protocol": "tcp", "service": "ssh"},
                {"port": 1521, "protocol": "tcp", "service": "oracle-tns"},
            ],
            "installed_software": [
                {"name": "oracle-database-ee", "version": "19.21"},
            ],
            "running_services": [
                {"name": "ora_pmon_PRODDB", "pid": 5000, "user": "oracle"},
                {"name": "ora_smon_PRODDB", "pid": 5001, "user": "oracle"},
                {"name": "tnslsnr", "pid": 4999, "user": "oracle"},
            ],
            "listening_services": [
                {"port": 1521, "pid": 4999, "process": "tnslsnr"},
            ],
            "app_server_type": None,
            "deployed_artifacts": [],
            "db_engine": "oracle",
            "db_version": "19.21",
            "databases": [
                {"name": "PRODDB", "size_mb": 150000, "schemas": ["PNL_SCHEMA", "REPORTING", "AUDIT"]},
            ],
            "config_files": [],
            "data_classifications": [
                {"path": "PRODDB.PNL_SCHEMA", "classification": "confidential", "confidence": 0.92},
            ],
            "business_context": {
                "purpose": "Primary Profit & Loss database storing financial transactions and reporting data",
                "department": "Finance",
                "criticality": "critical",
                "application_name": "P&L Database",
            },
            "human_verified": True,
            "tags": ["production", "finance", "database", "critical"],
            "custom_attributes": {},
        },
        {
            "_id": "asset-api-01",
            "hostname": "api-gateway-01",
            "ip_addresses": ["10.0.3.30"],
            "asset_type": "server",
            "status": "active",
            "os_family": "linux",
            "os_version": "Ubuntu 22.04 LTS",
            "discovered_at": now,
            "last_scanned": now,
            "scan_id": scan_id,
            "source": "infrastructure_scan",
            "open_ports": [
                {"port": 22, "protocol": "tcp", "service": "ssh"},
                {"port": 443, "protocol": "tcp", "service": "https"},
                {"port": 8080, "protocol": "tcp", "service": "http-alt"},
            ],
            "installed_software": [
                {"name": "nginx", "version": "1.24.0"},
                {"name": "nodejs", "version": "20.10.0"},
            ],
            "running_services": [
                {"name": "nginx", "pid": 2000, "user": "www-data"},
                {"name": "node", "pid": 2100, "user": "app"},
            ],
            "listening_services": [
                {"port": 443, "pid": 2000, "process": "nginx"},
                {"port": 8080, "pid": 2100, "process": "node"},
            ],
            "app_server_type": None,
            "deployed_artifacts": [],
            "db_engine": None,
            "databases": [],
            "config_files": [
                {"path": "/etc/nginx/sites-enabled/api.conf", "type": "nginx_config"},
                {"path": "/opt/api/config/production.json", "type": "app_config"},
            ],
            "data_classifications": [],
            "business_context": {
                "purpose": "REST API gateway serving financial reporting APIs",
                "department": "Engineering",
                "criticality": "high",
                "application_name": "Financial API Gateway",
            },
            "human_verified": True,
            "tags": ["production", "api", "gateway"],
            "custom_attributes": {},
        },
        {
            "_id": "asset-postgres-01",
            "hostname": "postgres-analytics-01",
            "ip_addresses": ["10.0.2.25"],
            "asset_type": "database",
            "status": "active",
            "os_family": "linux",
            "os_version": "Debian 12",
            "discovered_at": now,
            "last_scanned": now,
            "scan_id": scan_id,
            "source": "infrastructure_scan",
            "open_ports": [
                {"port": 22, "protocol": "tcp", "service": "ssh"},
                {"port": 5432, "protocol": "tcp", "service": "postgresql"},
            ],
            "installed_software": [
                {"name": "postgresql", "version": "16.1"},
            ],
            "running_services": [
                {"name": "postgresql", "pid": 3000, "user": "postgres"},
            ],
            "listening_services": [
                {"port": 5432, "pid": 3000, "process": "postgres"},
            ],
            "app_server_type": None,
            "deployed_artifacts": [],
            "db_engine": "postgresql",
            "db_version": "16.1",
            "databases": [
                {"name": "analytics", "size_mb": 50000, "schemas": ["public", "reports", "staging"]},
            ],
            "config_files": [],
            "data_classifications": [],
            "business_context": {
                "purpose": "Analytics data warehouse for financial reporting and dashboards",
                "department": "Finance",
                "criticality": "high",
            },
            "human_verified": False,
            "tags": ["production", "analytics", "database"],
            "custom_attributes": {},
        },
        {
            "_id": "asset-ldap-01",
            "hostname": "ad-dc-01",
            "ip_addresses": ["10.0.4.10"],
            "asset_type": "server",
            "status": "active",
            "os_family": "windows",
            "os_version": "Windows Server 2022",
            "discovered_at": now,
            "last_scanned": now,
            "scan_id": scan_id,
            "source": "infrastructure_scan",
            "open_ports": [
                {"port": 389, "protocol": "tcp", "service": "ldap"},
                {"port": 636, "protocol": "tcp", "service": "ldaps"},
                {"port": 3389, "protocol": "tcp", "service": "rdp"},
            ],
            "installed_software": [
                {"name": "Active Directory Domain Services", "version": "2022"},
            ],
            "running_services": [
                {"name": "NTDS", "pid": 800, "user": "SYSTEM"},
            ],
            "listening_services": [
                {"port": 389, "pid": 800, "process": "lsass.exe"},
                {"port": 636, "pid": 800, "process": "lsass.exe"},
            ],
            "app_server_type": None,
            "deployed_artifacts": [],
            "db_engine": None,
            "databases": [],
            "config_files": [],
            "data_classifications": [],
            "business_context": {
                "purpose": "Active Directory Domain Controller for enterprise authentication",
                "department": "IT",
                "criticality": "critical",
            },
            "human_verified": True,
            "tags": ["production", "infrastructure", "authentication"],
            "custom_attributes": {},
        },
        {
            "_id": "asset-tomcat-01",
            "hostname": "tomcat-hr-01",
            "ip_addresses": ["10.0.1.15"],
            "asset_type": "app_server",
            "status": "active",
            "os_family": "linux",
            "os_version": "CentOS Stream 9",
            "discovered_at": now,
            "last_scanned": now,
            "scan_id": scan_id,
            "source": "infrastructure_scan",
            "open_ports": [
                {"port": 22, "protocol": "tcp", "service": "ssh"},
                {"port": 8080, "protocol": "tcp", "service": "http"},
                {"port": 8443, "protocol": "tcp", "service": "https"},
            ],
            "installed_software": [
                {"name": "java-11-openjdk", "version": "11.0.21"},
                {"name": "apache-tomcat", "version": "9.0.83"},
            ],
            "running_services": [
                {"name": "java (Tomcat)", "pid": 6000, "user": "tomcat"},
            ],
            "listening_services": [
                {"port": 8080, "pid": 6000, "process": "java"},
                {"port": 8443, "pid": 6000, "process": "java"},
            ],
            "app_server_type": "tomcat",
            "deployed_artifacts": [
                {"name": "hr-portal.war", "path": "/opt/tomcat/webapps/", "size": 25000000},
            ],
            "db_engine": None,
            "databases": [],
            "config_files": [
                {"path": "/opt/tomcat/conf/server.xml", "type": "tomcat_config"},
                {"path": "/opt/tomcat/webapps/hr-portal/WEB-INF/web.xml", "type": "webapp_config"},
            ],
            "data_classifications": [],
            "business_context": {
                "purpose": "HR Portal web application for employee self-service",
                "department": "HR",
                "criticality": "medium",
            },
            "human_verified": False,
            "tags": ["production", "hr"],
            "custom_attributes": {},
        },
    ]

    relationships = [
        {
            "_id": "rel-wl-oracle",
            "source_asset_id": "asset-weblogic-01",
            "target_asset_id": "asset-oracle-01",
            "relationship_type": "queries",
            "direction": "outbound",
            "source_method": "config_parse",
            "evidence": [
                {"type": "config_file", "file": "/opt/weblogic/domains/prod/config/jdbc/pnl-ds.xml",
                 "connection_string": "jdbc:oracle:thin:@10.0.2.20:1521/PRODDB"}
            ],
            "confidence": 0.95,
            "protocol": "jdbc",
            "port": 1521,
            "endpoint": None,
            "request_count": None,
            "avg_latency_ms": None,
            "last_seen": now,
            "discovered_at": now,
            "scan_id": scan_id,
            "human_verified": True,
        },
        {
            "_id": "rel-api-wl",
            "source_asset_id": "asset-api-01",
            "target_asset_id": "asset-weblogic-01",
            "relationship_type": "calls_api",
            "direction": "outbound",
            "source_method": "network_connection",
            "evidence": [
                {"type": "active_connection", "remote_ip": "10.0.1.10", "remote_port": 7001}
            ],
            "confidence": 0.9,
            "protocol": "http",
            "port": 7001,
            "endpoint": "/pnl-webapp/api/v1/positions",
            "request_count": 15000,
            "avg_latency_ms": 45.2,
            "last_seen": now,
            "discovered_at": now,
            "scan_id": scan_id,
            "human_verified": False,
        },
        {
            "_id": "rel-api-postgres",
            "source_asset_id": "asset-api-01",
            "target_asset_id": "asset-postgres-01",
            "relationship_type": "queries",
            "direction": "outbound",
            "source_method": "config_parse",
            "evidence": [
                {"type": "config_file", "file": "/opt/api/config/production.json",
                 "connection_string": "postgresql://10.0.2.25:5432/analytics"}
            ],
            "confidence": 0.95,
            "protocol": "postgresql",
            "port": 5432,
            "endpoint": None,
            "request_count": 8000,
            "avg_latency_ms": 12.5,
            "last_seen": now,
            "discovered_at": now,
            "scan_id": scan_id,
            "human_verified": False,
        },
        {
            "_id": "rel-wl-ldap",
            "source_asset_id": "asset-weblogic-01",
            "target_asset_id": "asset-ldap-01",
            "relationship_type": "authenticates_via",
            "direction": "outbound",
            "source_method": "config_parse",
            "evidence": [
                {"type": "config_file", "file": "/opt/weblogic/domains/prod/config/config.xml",
                 "detail": "LDAP authenticator configured for AD"}
            ],
            "confidence": 0.85,
            "protocol": "ldaps",
            "port": 636,
            "endpoint": None,
            "request_count": None,
            "avg_latency_ms": None,
            "last_seen": now,
            "discovered_at": now,
            "scan_id": scan_id,
            "human_verified": False,
        },
        {
            "_id": "rel-tomcat-oracle",
            "source_asset_id": "asset-tomcat-01",
            "target_asset_id": "asset-oracle-01",
            "relationship_type": "queries",
            "direction": "outbound",
            "source_method": "config_parse",
            "evidence": [
                {"type": "config_file", "file": "/opt/tomcat/conf/server.xml",
                 "connection_string": "jdbc:oracle:thin:@10.0.2.20:1521/PRODDB"}
            ],
            "confidence": 0.95,
            "protocol": "jdbc",
            "port": 1521,
            "endpoint": None,
            "request_count": None,
            "avg_latency_ms": None,
            "last_seen": now,
            "discovered_at": now,
            "scan_id": scan_id,
            "human_verified": False,
        },
        {
            "_id": "rel-tomcat-ldap",
            "source_asset_id": "asset-tomcat-01",
            "target_asset_id": "asset-ldap-01",
            "relationship_type": "authenticates_via",
            "direction": "outbound",
            "source_method": "network_connection",
            "evidence": [
                {"type": "active_connection", "remote_ip": "10.0.4.10", "remote_port": 389}
            ],
            "confidence": 0.85,
            "protocol": "ldap",
            "port": 389,
            "endpoint": None,
            "request_count": None,
            "avg_latency_ms": None,
            "last_seen": now,
            "discovered_at": now,
            "scan_id": scan_id,
            "human_verified": False,
        },
    ]

    scan_doc = {
        "_id": scan_id,
        "scan_type": "full",
        "status": "completed",
        "targets": [{"host": a["ip_addresses"][0], "credential_id": ""} for a in assets],
        "scope": {},
        "total_targets": len(assets),
        "completed_targets": len(assets),
        "failed_targets": [],
        "assets_discovered": len(assets),
        "relationships_discovered": len(relationships),
        "new_assets": len(assets),
        "updated_assets": 0,
        "created_at": now - timedelta(hours=2),
        "started_at": now - timedelta(hours=2),
        "completed_at": now - timedelta(hours=1, minutes=45),
        "celery_task_id": "demo-task-id",
        "initiated_by": "manual",
        "schedule_id": None,
    }

    await db.assets.insert_many(assets)
    await db.relationships.insert_many(relationships)
    await db.scans.insert_one(scan_doc)

    print(f"Seeded {len(assets)} assets, {len(relationships)} relationships, 1 scan")
    client.close()


if __name__ == "__main__":
    asyncio.run(seed())
