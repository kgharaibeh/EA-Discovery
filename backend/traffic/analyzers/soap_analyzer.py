from traffic.plugins.base import RawFlow


class SOAPAnalyzer:
    def analyze(self, flows: list[RawFlow]) -> list[dict]:
        operations: dict[str, dict] = {}

        for flow in flows:
            if not flow.payload_sample:
                continue

            payload = flow.payload_sample.decode("utf-8", errors="ignore")
            if "<soap:" not in payload.lower() and "<soapenv:" not in payload.lower():
                continue

            operation = self._extract_operation(payload)
            if not operation:
                continue

            key = f"{flow.dst_ip}:{flow.dst_port}/{operation}"
            if key not in operations:
                operations[key] = {
                    "host": flow.dst_ip,
                    "port": flow.dst_port,
                    "operation": operation,
                    "protocol": "soap",
                    "consumers": set(),
                    "request_count": 0,
                }

            operations[key]["consumers"].add(flow.src_ip)
            operations[key]["request_count"] += 1

        result = []
        for op in operations.values():
            result.append({
                "host": op["host"],
                "port": op["port"],
                "operation": op["operation"],
                "protocol": "soap",
                "consumer_count": len(op["consumers"]),
                "consumers": list(op["consumers"]),
                "request_count": op["request_count"],
            })
        return result

    @staticmethod
    def _extract_operation(payload: str) -> str | None:
        body_start = payload.lower().find("<soap:body>")
        if body_start == -1:
            body_start = payload.lower().find("<soapenv:body>")
        if body_start == -1:
            return None

        after_body = payload[body_start:]
        tag_start = after_body.find("<", 1)
        if tag_start == -1:
            return None

        tag_end = after_body.find(">", tag_start)
        if tag_end == -1:
            return None

        tag = after_body[tag_start + 1:tag_end].split()[0]
        if ":" in tag:
            tag = tag.split(":")[1]
        return tag
