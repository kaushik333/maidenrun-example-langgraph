from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # logging
    log_dir: str = "logs"
    user_id: str = "local"
    log_level: str = "INFO"

    # LLM provider: whichever key is set picks the provider (see agent/llm.py)
    openrouter_api_key: str = ""
    openrouter_model: str = "openai/gpt-4o-mini"
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-haiku-4-5-20251001"
    azure_openai_api_key: str = ""
    azure_openai_endpoint: str = ""
    azure_openai_deployment: str = ""
    azure_openai_api_version: str = "2024-10-21"

    # optional web search provider
    tavily_api_key: str = ""

    # MaidenRun serves the agent UI from this port
    app_port: int = 8001


settings = Settings()
