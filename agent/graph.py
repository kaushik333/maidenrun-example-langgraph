import logging

from langgraph.graph import END, START, StateGraph

from agent.llm import get_llm
from agent.search import search
from agent.state import ResearchState

PLAN_PROMPT = """You are a research assistant. Break the topic below into exactly \
3 concise, distinct web search queries that together would surface a good \
overview of it. Reply with one query per line, no numbering, no extra text.

Topic: {topic}"""

SYNTHESIZE_PROMPT = """You are a research assistant. Using only the sources below, \
write a well-structured markdown report on the topic. Use headings, keep it \
concise, and cite sources inline as [n] linking to their URL. If the sources \
are thin or conflicting, say so explicitly rather than guessing.

Topic: {topic}

Sources:
{sources}"""


def build_graph(logger: logging.Logger):
    def plan_node(state: ResearchState) -> dict:
        llm = get_llm(temperature=0.2)
        response = llm.invoke(PLAN_PROMPT.format(topic=state["topic"]))
        queries = [line.strip("-* ").strip() for line in response.content.splitlines() if line.strip()]
        queries = queries[:3] or [state["topic"]]
        logger.info("planned queries for topic=%r: %s", state["topic"], queries)
        return {"queries": queries}

    def search_node(state: ResearchState) -> dict:
        findings = [
            {"query": query, **result}
            for query in state["queries"]
            for result in search(query, logger)
        ]
        logger.info("collected %d findings across %d queries", len(findings), len(state["queries"]))
        return {"findings": findings}

    def synthesize_node(state: ResearchState) -> dict:
        sources = "\n".join(
            f"[{i}] {f['title']} — {f['url']}\n{f['snippet']}" for i, f in enumerate(state["findings"], 1)
        ) or "(no search results found)"
        llm = get_llm(temperature=0.3)
        response = llm.invoke(SYNTHESIZE_PROMPT.format(topic=state["topic"], sources=sources))
        logger.info("synthesized report (%d chars)", len(response.content))
        return {"report": response.content}

    graph = StateGraph(ResearchState)
    graph.add_node("plan", plan_node)
    graph.add_node("search", search_node)
    graph.add_node("synthesize", synthesize_node)
    graph.add_edge(START, "plan")
    graph.add_edge("plan", "search")
    graph.add_edge("search", "synthesize")
    graph.add_edge("synthesize", END)
    return graph.compile()
