import asyncio
from datetime import datetime

from tasks.celery_app import celery_app


def _run_async(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="tasks.capture_traffic")
def capture_traffic(host: str, credential_id: str, plugin_name: str = "tcpdump", duration: int = 60):
    _run_async(_capture_traffic_async(host, credential_id, plugin_name, duration))


async def _capture_traffic_async(host: str, credential_id: str, plugin_name: str, duration: int):
    from app.core.database import connect_db, close_db, get_database
    from scanner.connectors.ssh_connector import SSHConnector
    from credentials.manager import CredentialManager
    from traffic.engine import TrafficAnalysisEngine

    await connect_db()
    try:
        cred_manager = CredentialManager()
        creds = await cred_manager.get_credential(credential_id)

        connector = SSHConnector()
        await connector.connect(host, 22, creds)

        try:
            engine = TrafficAnalysisEngine()
            result = await engine.capture_and_analyze(
                connector=connector,
                plugin_name=plugin_name,
                duration_seconds=duration,
            )

            db = get_database()
            capture_doc = {
                "_id": str(hash(f"{host}:{datetime.utcnow().isoformat()}")),
                "scan_id": "",
                "source_plugin": plugin_name,
                "target_host": host,
                "capture_duration_seconds": duration,
                "flows": result.get("flows", []),
                "api_endpoints_discovered": result.get("api_endpoints", []),
                "captured_at": datetime.utcnow(),
            }
            await db.traffic_captures.insert_one(capture_doc)
        finally:
            await connector.disconnect()
    finally:
        await close_db()
