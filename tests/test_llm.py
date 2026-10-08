import pytest

from agent import llm
from agent.config import settings


@pytest.fixture(autouse=True)
def clear_provider_keys():
    keys = ("openrouter_api_key", "openai_api_key", "anthropic_api_key", "azure_openai_api_key")
    original = {k: getattr(settings, k) for k in keys}
    for k in keys:
        setattr(settings, k, "")
    yield
    for k, v in original.items():
        setattr(settings, k, v)


def test_no_provider_configured_raises():
    with pytest.raises(RuntimeError, match="No LLM provider configured"):
        llm.get_llm()


def test_openai_key_selects_chat_openai():
    settings.openai_api_key = "sk-test"
    model = llm.get_llm()
    assert type(model).__name__ == "ChatOpenAI"


def test_anthropic_key_takes_precedence_over_openai():
    settings.openai_api_key = "sk-test"
    settings.anthropic_api_key = "anthropic-test"
    model = llm.get_llm()
    assert type(model).__name__ == "ChatAnthropic"


def test_openrouter_key_selects_chat_openai_pointed_at_openrouter():
    settings.openrouter_api_key = "sk-or-test"
    settings.anthropic_api_key = "anthropic-test"
    model = llm.get_llm()
    assert type(model).__name__ == "ChatOpenAI"
    assert model.openai_api_base == settings.openrouter_base_url
    assert model.model_name == settings.openrouter_model
