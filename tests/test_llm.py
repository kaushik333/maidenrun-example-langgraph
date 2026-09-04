import pytest

from agent import llm
from agent.config import settings


@pytest.fixture(autouse=True)
def clear_provider_keys():
    original = (settings.openai_api_key, settings.anthropic_api_key, settings.azure_openai_api_key)
    settings.openai_api_key = ""
    settings.anthropic_api_key = ""
    settings.azure_openai_api_key = ""
    yield
    settings.openai_api_key, settings.anthropic_api_key, settings.azure_openai_api_key = original


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
