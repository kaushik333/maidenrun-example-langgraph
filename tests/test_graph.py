import logging
from types import SimpleNamespace

from agent.graph import build_graph


class FakeLLM:
    """Returns queued responses in order, one per .invoke() call."""

    def __init__(self, responses: list[str]):
        self._responses = list(responses)

    def invoke(self, _prompt):
        return SimpleNamespace(content=self._responses.pop(0))


def test_graph_runs_plan_search_synthesize(monkeypatch):
    fake_llm = FakeLLM(
        [
            "query one\nquery two",  # plan
            "# Report\nSynthesized findings [1].",  # synthesize
        ]
    )
    monkeypatch.setattr("agent.graph.get_llm", lambda temperature=0.3: fake_llm)
    monkeypatch.setattr(
        "agent.graph.search",
        lambda query, logger: [{"title": f"Result for {query}", "url": "https://x.test", "snippet": "s"}],
    )

    graph = build_graph(logging.getLogger("test"))
    result = graph.invoke({"topic": "test topic", "queries": [], "findings": [], "report": ""})

    assert result["queries"] == ["query one", "query two"]
    assert len(result["findings"]) == 2
    assert result["findings"][0]["query"] == "query one"
    assert result["report"] == "# Report\nSynthesized findings [1]."


def test_graph_handles_empty_search_results(monkeypatch):
    fake_llm = FakeLLM(["only query", "# Report\nNo sources found."])
    monkeypatch.setattr("agent.graph.get_llm", lambda temperature=0.3: fake_llm)
    monkeypatch.setattr("agent.graph.search", lambda query, logger: [])

    graph = build_graph(logging.getLogger("test"))
    result = graph.invoke({"topic": "obscure topic", "queries": [], "findings": [], "report": ""})

    assert result["findings"] == []
    assert "No sources found" in result["report"]
