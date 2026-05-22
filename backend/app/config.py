from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_uri: str = "mongodb://localhost:27017/ea_discovery"
    mongodb_database: str = "ea_discovery"

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_secret_key: str = "change-me-in-production"

    credential_backend: str = "encrypted_file"
    credential_master_key: str = "change-me-32-byte-key-for-aes256"

    vault_url: str = "http://vault:8200"
    vault_token: str = ""

    llm_provider: str = "ollama"
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    ollama_url: str = "http://ollama:11434"

    scan_concurrency: int = 10
    scan_timeout: int = 300
    ssh_default_port: int = 22
    winrm_default_port: int = 5985

    ldap_url: str = ""
    ldap_base_dn: str = ""
    ldap_bind_dn: str = ""
    ldap_bind_password: str = ""

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
