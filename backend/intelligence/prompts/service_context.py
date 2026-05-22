import json

SERVICE_CONTEXT_SYSTEM = """You are an enterprise architecture analyst. Given details about a discovered IT asset (hostname, running services, installed software, open ports, configuration files, database schemas, network connections), infer the business purpose of this asset.

Respond ONLY in valid JSON format:
{
  "purpose": "Brief description of what this system does in business terms",
  "department": "Most likely owning department (Finance, Engineering, HR, Operations, Marketing, IT, Security, etc.)",
  "criticality": "low|medium|high|critical",
  "application_name": "Inferred application name if identifiable, otherwise null",
  "data_sensitivity": "public|internal|confidential|restricted",
  "reasoning": "2-3 sentences explaining your inference chain"
}"""


def build_service_context_prompt(asset: dict) -> str:
    context_parts = [f"Hostname: {asset.get('hostname', 'unknown')}"]

    if asset.get("os_family"):
        context_parts.append(f"OS: {asset['os_family']} {asset.get('os_version', '')}")

    if asset.get("open_ports"):
        ports = [f"{p['port']}/{p.get('protocol', 'tcp')}" for p in asset["open_ports"][:20]]
        context_parts.append(f"Open ports: {', '.join(ports)}")

    if asset.get("listening_services"):
        listeners = [
            f"{s.get('process', 'unknown')} on port {s.get('port', '?')}"
            for s in asset["listening_services"][:15]
        ]
        context_parts.append(f"Listening services: {', '.join(listeners)}")

    if asset.get("running_services"):
        services = [s.get("name", "unknown") for s in asset["running_services"][:20]]
        context_parts.append(f"Running services: {', '.join(services)}")

    if asset.get("installed_software"):
        software = [f"{s['name']} {s.get('version', '')}" for s in asset["installed_software"][:20]]
        context_parts.append(f"Installed software: {', '.join(software)}")

    if asset.get("app_server_type"):
        context_parts.append(f"Application server: {asset['app_server_type']}")

    if asset.get("deployed_artifacts"):
        artifacts = [a.get("name", "unknown") for a in asset["deployed_artifacts"][:10]]
        context_parts.append(f"Deployed artifacts: {', '.join(artifacts)}")

    if asset.get("db_engine"):
        context_parts.append(f"Database engine: {asset['db_engine']} {asset.get('db_version', '')}")
        if asset.get("databases"):
            db_names = [d.get("name", "unknown") for d in asset["databases"][:10]]
            context_parts.append(f"Databases: {', '.join(db_names)}")

    if asset.get("config_files"):
        configs = [c.get("path", "unknown") for c in asset["config_files"][:10]]
        context_parts.append(f"Config files: {', '.join(configs)}")

    return "\n".join(context_parts)
