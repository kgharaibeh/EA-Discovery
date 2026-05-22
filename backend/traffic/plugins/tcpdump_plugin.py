import struct
from datetime import datetime

from traffic.plugins.base import AbstractTrafficPlugin, RawFlow


class TcpdumpPlugin(AbstractTrafficPlugin):
    @property
    def name(self) -> str:
        return "tcpdump"

    async def capture(
        self,
        connector,
        interface: str,
        duration_seconds: int,
        filter_expr: str | None = None,
    ) -> list[RawFlow]:
        filter_part = f" {filter_expr}" if filter_expr else ""
        cmd = (
            f"timeout {duration_seconds} tcpdump -nn -i {interface} "
            f"-c 10000 -l{filter_part} 2>/dev/null"
        )
        result = await connector.execute(cmd, timeout=duration_seconds + 10)
        return self._parse_tcpdump_output(result.stdout)

    async def parse_file(self, file_path: str) -> list[RawFlow]:
        return []

    def _parse_tcpdump_output(self, output: str) -> list[RawFlow]:
        flows: list[RawFlow] = []
        for line in output.strip().split("\n"):
            if not line:
                continue
            flow = self._parse_line(line)
            if flow:
                flows.append(flow)
        return flows

    def _parse_line(self, line: str) -> RawFlow | None:
        try:
            parts = line.split()
            if len(parts) < 5:
                return None

            src_part = None
            dst_part = None
            for i, p in enumerate(parts):
                if p == ">":
                    src_part = parts[i - 1].rstrip(":")
                    dst_part = parts[i + 1].rstrip(":")
                    break

            if not src_part or not dst_part:
                return None

            src_ip, src_port = self._parse_host_port(src_part)
            dst_ip, dst_port = self._parse_host_port(dst_part)

            return RawFlow(
                src_ip=src_ip,
                src_port=src_port,
                dst_ip=dst_ip,
                dst_port=dst_port,
                protocol="tcp",
            )
        except (ValueError, IndexError):
            return None

    @staticmethod
    def _parse_host_port(host_port: str) -> tuple[str, int]:
        last_dot = host_port.rfind(".")
        if last_dot == -1:
            return host_port, 0
        ip = host_port[:last_dot]
        port_str = host_port[last_dot + 1:]
        try:
            return ip, int(port_str)
        except ValueError:
            return host_port, 0
