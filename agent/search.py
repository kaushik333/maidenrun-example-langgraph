import logging

from ddgs import DDGS
from tavily import TavilyClient

from agent.config import settings

MAX_RESULTS = 4


def _duckduckgo_text(query: str) -> list[dict]:
    return DDGS().text(query, max_results=MAX_RESULTS)


def search(query: str, logger: logging.Logger) -> list[dict]:
    """Web search, normalized to [{title, url, snippet}, ...].

    Uses Tavily when TAVILY_API_KEY is set (through MaidenRun's "Additional
    environment variables"); otherwise falls back to DuckDuckGo, which needs
    no key so the agent works out of the box.
    """
    if settings.tavily_api_key:
        client = TavilyClient(api_key=settings.tavily_api_key)
        response = client.search(query, max_results=MAX_RESULTS)
        return [
            {"title": r.get("title", ""), "url": r.get("url", ""), "snippet": r.get("content", "")}
            for r in response.get("results", [])
        ]

    try:
        results = _duckduckgo_text(query)
    except Exception as exc:  # DuckDuckGo rate-limits/blocks intermittently
        logger.warning("search failed for %r: %s", query, exc)
        return []

    return [
        {"title": r.get("title", ""), "url": r.get("href", ""), "snippet": r.get("body", "")}
        for r in results
    ]
