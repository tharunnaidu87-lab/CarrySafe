from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "sqlite:///./carrysafe.db"
    environment: str = "local"
    allowed_hosts: str = "localhost,127.0.0.1,testserver,terminal.local"
    allowed_origins: str = "http://localhost:8000,http://127.0.0.1:8000,http://localhost:4173,http://127.0.0.1:4173,http://terminal.local:4173"
    mcp_url: str = "http://127.0.0.1:8000/mcp"
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""
    timezone: str = "Asia/Kolkata"


settings = Settings()
