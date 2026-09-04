import logging

from agent import search
from agent.config import settings


def test_duckduckgo_fallback_when_no_tavily_key(monkeypatch):
    settings.tavily_api_key = ""
    monkeypatch.setattr(
        "agent.search._duckduckgo_text",
        lambda query: [{"title": "T", "href": "https://x.test", "body": "snippet"}],
    )
    results = search.search("test query", logging.getLogger("test"))
    assert results == [{"title": "T", "url": "https://x.test", "snippet": "snippet"}]


def test_duckduckgo_failure_returns_empty_list(monkeypatch):
    settings.tavily_api_key = ""

    def raise_error(query):
        raise RuntimeError("rate limited")

    monkeypatch.setattr("agent.search._duckduckgo_text", raise_error)
    results = search.search("test query", logging.getLogger("test"))
    assert results == []


def test_tavily_used_when_key_present(monkeypatch):
    settings.tavily_api_key = "tvly-test"

    class FakeTavilyClient:
        def __init__(self, api_key):
            self.api_key = api_key

        def search(self, query, max_results):
            return {"results": [{"title": "T", "url": "https://x.test", "content": "snippet"}]}

    monkeypatch.setattr("agent.search.TavilyClient", FakeTavilyClient)
    results = search.search("test query", logging.getLogger("test"))
    settings.tavily_api_key = ""
    assert results == [{"title": "T", "url": "https://x.test", "snippet": "snippet"}]
