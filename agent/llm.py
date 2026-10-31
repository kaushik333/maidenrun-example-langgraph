from langchain_core.language_models.chat_models import BaseChatModel

from agent.config import settings


def get_llm(temperature: float = 0.3) -> BaseChatModel:
    """Picks a provider from whichever API key env var is set. Exactly one of
    OPENROUTER_API_KEY / OPENAI_API_KEY / ANTHROPIC_API_KEY / AZURE_OPENAI_API_KEY
    is expected."""
    if settings.openrouter_api_key:
        from langchain_openai import ChatOpenAI

        # OpenRouter speaks the OpenAI chat API, so ChatOpenAI just needs its base URL.
        return ChatOpenAI(
            model=settings.openrouter_model,
            api_key=settings.openrouter_api_key,
            base_url=settings.openrouter_base_url,
            temperature=temperature,
        )

    if settings.anthropic_api_key:
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=settings.anthropic_model, api_key=settings.anthropic_api_key, temperature=temperature
        )

    if settings.openai_api_key:
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=settings.openai_model, api_key=settings.openai_api_key, temperature=temperature)

    if settings.azure_openai_api_key:
        from langchain_openai import AzureChatOpenAI

        return AzureChatOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            azure_deployment=settings.azure_openai_deployment,
            api_version=settings.azure_openai_api_version,
            api_key=settings.azure_openai_api_key,
            temperature=temperature,
        )

    raise RuntimeError(
        "No LLM provider configured. Set OPENROUTER_API_KEY, OPENAI_API_KEY, "
        "ANTHROPIC_API_KEY, or AZURE_OPENAI_API_KEY (see .env.example)."
    )
