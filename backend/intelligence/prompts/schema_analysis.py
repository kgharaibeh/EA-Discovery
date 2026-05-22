SCHEMA_ANALYSIS_SYSTEM = """You are a database analyst. Given database schema information (table names, column names, indexes), infer the business purpose of the database.

Respond ONLY in valid JSON format:
{
  "purpose": "What business domain this database serves",
  "domain": "finance|hr|crm|inventory|analytics|logging|authentication|content|other",
  "key_entities": ["list", "of", "main", "business", "entities"],
  "data_sensitivity": "public|internal|confidential|restricted",
  "reasoning": "Brief explanation"
}"""


def build_schema_analysis_prompt(db_info: dict) -> str:
    parts = [f"Database: {db_info.get('name', 'unknown')}"]
    parts.append(f"Engine: {db_info.get('engine', 'unknown')}")

    if db_info.get("tables"):
        parts.append("\nTables:")
        for table in db_info["tables"][:30]:
            cols = ", ".join(table.get("columns", [])[:10])
            parts.append(f"  {table.get('name', '?')}: [{cols}]")

    return "\n".join(parts)
