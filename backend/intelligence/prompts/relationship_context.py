RELATIONSHIP_CONTEXT_SYSTEM = """You are an enterprise architecture analyst. Given information about two connected IT assets and the nature of their connection, infer the business purpose of this relationship.

Respond ONLY in valid JSON format:
{
  "purpose": "What business function this connection serves",
  "data_flow_description": "What data likely flows between these systems",
  "direction": "unidirectional|bidirectional",
  "criticality": "low|medium|high|critical",
  "reasoning": "2-3 sentences explaining your inference"
}"""


def build_relationship_context_prompt(
    source_asset: dict,
    target_asset: dict,
    relationship: dict,
) -> str:
    parts = [
        f"Source: {source_asset.get('hostname', 'unknown')} ({source_asset.get('asset_type', 'unknown')})",
    ]

    if source_asset.get("business_context"):
        parts.append(f"  Business context: {source_asset['business_context'].get('purpose', 'unknown')}")

    parts.append(
        f"Target: {target_asset.get('hostname', 'unknown')} ({target_asset.get('asset_type', 'unknown')})"
    )

    if target_asset.get("business_context"):
        parts.append(f"  Business context: {target_asset['business_context'].get('purpose', 'unknown')}")

    parts.append(f"Connection type: {relationship.get('relationship_type', 'unknown')}")
    parts.append(f"Protocol: {relationship.get('protocol', 'unknown')}")

    if relationship.get("port"):
        parts.append(f"Port: {relationship['port']}")

    if relationship.get("endpoint"):
        parts.append(f"Endpoint: {relationship['endpoint']}")

    if relationship.get("evidence"):
        for ev in relationship["evidence"][:3]:
            parts.append(f"Evidence: {ev}")

    return "\n".join(parts)
