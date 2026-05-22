from datetime import datetime

from traffic.plugins.base import AbstractTrafficPlugin, RawFlow
from traffic.analyzers.http_analyzer import HTTPAnalyzer
from traffic.analyzers.database_analyzer import DatabaseAnalyzer
from traffic.analyzers.soap_analyzer import SOAPAnalyzer
from traffic.analyzers.generic_analyzer import GenericAnalyzer
from traffic.plugin_registry import traffic_plugin_registry


class TrafficAnalysisEngine:
    def __init__(self):
        self.http_analyzer = HTTPAnalyzer()
        self.db_analyzer = DatabaseAnalyzer()
        self.soap_analyzer = SOAPAnalyzer()
        self.generic_analyzer = GenericAnalyzer()

    async def capture_and_analyze(
        self,
        connector,
        plugin_name: str,
        interface: str = "any",
        duration_seconds: int = 60,
        filter_expr: str | None = None,
    ) -> dict:
        plugin: AbstractTrafficPlugin = traffic_plugin_registry.create(plugin_name)

        flows = await plugin.capture(
            connector=connector,
            interface=interface,
            duration_seconds=duration_seconds,
            filter_expr=filter_expr,
        )

        return self._analyze_flows(flows, plugin_name)

    def _analyze_flows(self, flows: list[RawFlow], source_plugin: str) -> dict:
        http_endpoints = self.http_analyzer.analyze(flows)
        db_connections = self.db_analyzer.analyze(flows)
        soap_operations = self.soap_analyzer.analyze(flows)
        generic_connections = self.generic_analyzer.analyze(flows)

        aggregated_flows = []
        seen: set[str] = set()
        for flow in flows:
            key = f"{flow.src_ip}:{flow.src_port}->{flow.dst_ip}:{flow.dst_port}"
            if key not in seen:
                seen.add(key)
                aggregated_flows.append({
                    "src_ip": flow.src_ip,
                    "src_port": flow.src_port,
                    "dst_ip": flow.dst_ip,
                    "dst_port": flow.dst_port,
                    "protocol": flow.protocol,
                    "method": flow.method,
                    "path": flow.path,
                    "bytes_transferred": flow.bytes_transferred,
                })

        return {
            "source_plugin": source_plugin,
            "total_flows": len(flows),
            "unique_connections": len(aggregated_flows),
            "flows": aggregated_flows[:1000],
            "api_endpoints": http_endpoints,
            "db_connections": db_connections,
            "soap_operations": soap_operations,
            "generic_connections": generic_connections,
            "captured_at": datetime.utcnow().isoformat(),
        }
