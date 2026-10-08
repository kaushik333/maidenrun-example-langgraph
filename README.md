# Research Agent

A minimal LangGraph research agent. Given a topic, it plans a few search
queries, runs them against the web, and synthesizes a cited markdown report.

It exists as a **test fixture** for [agentdock](../agentdock),
the BYOC agent-deploy-and-feedback platform described in
[IDEA.md](../IDEA.md). It is deliberately simple and already conforms to
that platform's entry-point contract: a single root `docker-compose.yml`,
agent UI on host port 8001, and an LLM API key read from a fixed env var
name — deliberately not declared in the compose file, since AgentDock
injects it.

## Installation

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/).

```bash
cp .env.example .env
# edit .env: set OPENROUTER_API_KEY (or OPENAI_API_KEY / ANTHROPIC_API_KEY / AZURE_OPENAI_*)
uv sync
uv run python app.py
```

Open http://localhost:8001.

### Docker

```bash
docker compose up --build
```

### Tests

```bash
uv sync --extra dev
uv run pytest
```

Tests mock the LLM and search calls, so they run offline with no API key.

## Project structure

```
research-agent/
├── app.py                    # Gradio UI, entrypoint, binds 0.0.0.0:8001
├── agent/
│   ├── config.py              # .env-driven settings (pydantic-settings)
│   ├── logging_setup.py       # per-run logger: logs/<user-id>/<run-id>/agent.log
│   ├── llm.py                 # picks a provider from whichever API key is set
│   ├── search.py               # Tavily if TAVILY_API_KEY is set, else DuckDuckGo
│   ├── state.py                 # typed LangGraph state
│   └── graph.py                  # the plan -> search -> synthesize graph
├── tests/                      # offline unit tests (mocked LLM + search)
├── feedback-questions.yaml      # sample custom questionnaire for the platform's :8002 form
├── docker-compose.yml       # entry point: builds the Dockerfile, serves :8001
├── Dockerfile
├── pyproject.toml
└── .env.example
```

## Architecture

```
┌─────────────────────────┐
│  Gradio UI  (app.py)    │   :8001, one text input: topic
└────────────┬────────────┘
             │ topic
             ▼
┌─────────────────────────┐
│  plan                   │   LLM: topic -> 3 search queries
└────────────┬────────────┘
             │ queries
             ▼
┌─────────────────────────┐
│  search                 │   Tavily (if TAVILY_API_KEY) or DuckDuckGo
└────────────┬────────────┘
             │ findings
             ▼
┌─────────────────────────┐
│  synthesize             │   LLM: findings -> cited markdown report
└────────────┬────────────┘
             │ report
             ▼
┌─────────────────────────┐
│  Gradio UI  (app.py)    │   renders the report
└─────────────────────────┘
```

`plan`, `search`, and `synthesize` are the three nodes of the LangGraph
`StateGraph` in `agent/graph.py`, run in that fixed order.

Each run writes to `logs/<user-id>/<run-id>/agent.log` (`user-id` defaults
to `local`; there's no auth in this demo).

## Components

**`agent/graph.py`** — a 3-node `StateGraph` (`ResearchState`: topic,
queries, findings, report). `plan` asks the LLM for 3 search queries,
`search` runs them, `synthesize` asks the LLM to write a markdown report
grounded only in what was found. Nodes are plain closures over a
per-run logger, so the graph has no hidden global state.

**`agent/llm.py`** — provider selection follows the platform's fixed
dropdown-to-env-var convention: `OPENROUTER_API_KEY` → any OpenRouter model
(`OPENROUTER_MODEL`), `ANTHROPIC_API_KEY` → Claude, `OPENAI_API_KEY` → GPT,
`AZURE_OPENAI_API_KEY` → Azure OpenAI. Exactly one
is expected to be set; if none are, it fails with a clear error rather than
guessing.

**`agent/search.py`** — DuckDuckGo by default (no key required, so the
agent works out of the box); switches to Tavily if `TAVILY_API_KEY` is
set, demonstrating the platform's "additional environment variables"
mechanism. DuckDuckGo failures are logged and treated as zero results
rather than crashing the run.

**`feedback-questions.yaml`** — a sample custom questionnaire, present so
a real deploy through the platform exercises the `:8002` custom-form path
instead of the default questionnaire.

## Known limitations

- DuckDuckGo search is unauthenticated and can intermittently rate-limit;
  set `TAVILY_API_KEY` for more reliable search.
- No conversation memory — every submission is a fresh, independent run.
- This is a test fixture, not a reference implementation of a "good"
  research agent; the graph is intentionally linear and unoptimized.
