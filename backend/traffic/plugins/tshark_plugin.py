import json

from traffic.plugins.base import AbstractTrafficPlugin, RawFlow


class TsharkPlugin(AbstractTrafficPlugin):
    @property
    def name(self) -> str:
        return "tshark"

    async def capture(
        self,
        connector,
        interface: str,
        duration_seconds: int,
        filter_expr: str | None = None,
    ) -> list[RawFlow]:
        filter_part = f" -f '{filter_expr}'" if filter_expr else ""
        cmd = (
            f"timeout {duration_seconds} tshark -i {interface} "
            f"-c 5000 -T json -l{filter_part} 2>/dev/null"
        )
        result = await connector.execute(cmd, timeout=duration_seconds + 10)
        return self._parse_json_output(result.stdout)

    async def parse_file(self, file_path: str) -> list[RawFlow]:
        return []

    def _parse_json_output(self, output: str) -> list[RawFlow]:
        flows: list[RawFlow] = []
        try:
            packets = json.loads(output)
        except json.JSONDecodeError:
            return flows

        for pkt in packets:
            layers = pkt.get("_source", {}).get("layers", {})
            ip_layer = layers.get("ip", {})
            tcp_layer = layers.get("tcp", {})
            http_layer = layers.get("http", {})

            src_ip = ip_layer.get("ip.src", "")
            dst_ip = ip_layer.get("ip.dst", "")
            src_port = int(tcp_layer.get("tcp.srcport", 0))
            dst_port = int(tcp_layer.get("tcp.dstport", 0))

            flow = RawFlow(
                src_ip=src_ip,
                src_port=src_port,
                dst_ip=dst_ip,
                dst_port=dst_port,
                protocol="tcp",
            )

            if http_layer:
                flow.method = http_layer.get("http.request.method")
                flow.path = http_layer.get("http.request.uri")
                flow.status_code = int(http_layer.get("http.response.code", 0)) or None
                flow.content_type = http_layer.get("http.content_type")
                flow.protocol = "http"

            flows.append(flow)

        return flows
