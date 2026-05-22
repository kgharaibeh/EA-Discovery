from app.services.relationship_service import RelationshipService


class ExportService:
    def __init__(self, relationship_service: RelationshipService):
        self.relationship_service = relationship_service

    async def export_drawio(
        self,
        asset_types: list[str] | None = None,
        relationship_types: list[str] | None = None,
    ) -> str:
        topology = await self.relationship_service.get_topology(
            asset_types=asset_types,
            relationship_types=relationship_types,
        )

        xml_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<mxfile>',
            '<diagram name="EA Discovery">',
            '<mxGraphModel>',
            '<root>',
            '<mxCell id="0"/>',
            '<mxCell id="1" parent="0"/>',
        ]

        for i, node in enumerate(topology.nodes):
            x = (i % 5) * 200 + 50
            y = (i // 5) * 150 + 50
            style = self._get_node_style(node.asset_type)
            label = f"{node.hostname}\\n({node.asset_type})"
            xml_parts.append(
                f'<mxCell id="n_{node.id}" value="{label}" style="{style}" '
                f'vertex="1" parent="1">'
                f'<mxGeometry x="{x}" y="{y}" width="140" height="80" as="geometry"/>'
                f'</mxCell>'
            )

        for edge in topology.edges:
            style = self._get_edge_style(edge.relationship_type)
            label = edge.relationship_type
            xml_parts.append(
                f'<mxCell id="e_{edge.id}" value="{label}" style="{style}" '
                f'edge="1" parent="1" source="n_{edge.source}" target="n_{edge.target}">'
                f'<mxGeometry relative="1" as="geometry"/>'
                f'</mxCell>'
            )

        xml_parts.extend(['</root>', '</mxGraphModel>', '</diagram>', '</mxfile>'])
        return "\n".join(xml_parts)

    async def export_csv(self, asset_types: list[str] | None = None) -> str:
        topology = await self.relationship_service.get_topology(asset_types=asset_types)
        lines = ["source_hostname,source_type,target_hostname,target_type,relationship_type,protocol,port"]
        node_map = {n.id: n for n in topology.nodes}
        for edge in topology.edges:
            src = node_map.get(edge.source)
            tgt = node_map.get(edge.target)
            if src and tgt:
                lines.append(
                    f"{src.hostname},{src.asset_type},{tgt.hostname},{tgt.asset_type},"
                    f"{edge.relationship_type},{edge.protocol or ''},{edge.port or ''}"
                )
        return "\n".join(lines)

    @staticmethod
    def _get_node_style(asset_type: str) -> str:
        styles = {
            "server": "rounded=1;whiteSpace=wrap;fillColor=#dae8fc;strokeColor=#6c8ebf;",
            "database": "shape=cylinder3;whiteSpace=wrap;fillColor=#d5e8d4;strokeColor=#82b366;",
            "application": "rounded=1;whiteSpace=wrap;fillColor=#fff2cc;strokeColor=#d6b656;",
            "app_server": "rounded=1;whiteSpace=wrap;fillColor=#e1d5e7;strokeColor=#9673a6;",
            "api_endpoint": "shape=hexagon;whiteSpace=wrap;fillColor=#f8cecc;strokeColor=#b85450;",
        }
        return styles.get(asset_type, "rounded=1;whiteSpace=wrap;")

    @staticmethod
    def _get_edge_style(rel_type: str) -> str:
        styles = {
            "queries": "strokeColor=#0000FF;dashed=1;",
            "calls_api": "strokeColor=#00AA00;",
            "hosts": "strokeColor=#888888;dashed=1;dashPattern=1 2;",
            "connects_to": "strokeColor=#AAAAAA;",
            "depends_on": "strokeColor=#FF6600;",
        }
        return styles.get(rel_type, "strokeColor=#000000;")
