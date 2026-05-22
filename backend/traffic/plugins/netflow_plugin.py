from traffic.plugins.base import AbstractTrafficPlugin, RawFlow


class NetFlowPlugin(AbstractTrafficPlugin):
    @property
    def name(self) -> str:
        return "netflow"

    async def capture(
        self,
        connector,
        interface: str,
        duration_seconds: int,
        filter_expr: str | None = None,
    ) -> list[RawFlow]:
        cmd = f"nfdump -r /var/cache/nfdump/ -o csv 2>/dev/null | head -5000"
        result = await connector.execute(cmd, timeout=30)
        return self._parse_nfdump_csv(result.stdout)

    async def parse_file(self, file_path: str) -> list[RawFlow]:
        return []

    def _parse_nfdump_csv(self, output: str) -> list[RawFlow]:
        flows: list[RawFlow] = []
        lines = output.strip().split("\n")
        for line in lines[1:]:
            parts = line.split(",")
            if len(parts) < 8:
                continue
            try:
                flows.append(RawFlow(
                    src_ip=parts[3].strip(),
                    src_port=int(parts[5].strip()),
                    dst_ip=parts[4].strip(),
                    dst_port=int(parts[6].strip()),
                    protocol=parts[7].strip().lower(),
                    bytes_transferred=int(parts[11].strip()) if len(parts) > 11 else 0,
                ))
            except (ValueError, IndexError):
                continue
        return flows
