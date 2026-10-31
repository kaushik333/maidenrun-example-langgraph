# Research Agent: a LangGraph agent for MaidenRun

A [LangGraph](https://langchain-ai.github.io/langgraph/) research agent. Give it a topic: it plans three search queries, runs them on the web, and writes a cited markdown report. The UI is [Gradio](https://gradio.app), and the model is any [OpenRouter](https://openrouter.ai) model (OpenAI, Anthropic and Azure OpenAI keys work too).

It's an example for [MaidenRun](https://github.com/kaushik333/MaidenRun): a root `docker-compose.yml` with the UI on port 8001.

## Deploy with MaidenRun

1. Paste this repo's URL into MaidenRun and click **Check**.
2. Under **LLM connection**, set the API key env var name to `OPENROUTER_API_KEY` and paste your key.
3. Click **Deploy**. The app comes up on port 8001.

Optional: add `TAVILY_API_KEY` under **Additional environment variables** for more reliable search (it falls back to DuckDuckGo without it), and deploy a feedback stack with [feedback-questions.json](feedback-questions.json).

## Run locally

```bash
cp .env.example .env        # add your OPENROUTER_API_KEY
docker compose up --build   # http://localhost:8001
```

Without Docker: `uv sync && uv run python app.py`

Tests run offline, with the LLM and search mocked: `uv sync --extra dev && uv run pytest`

## How it works

```
topic → plan (LLM: 3 search queries) → search (Tavily or DuckDuckGo) → synthesize (LLM: cited report)
```

The three steps are the nodes of a LangGraph `StateGraph` in `agent/graph.py`, run in that order.

## Files

```
app.py                  Gradio UI
agent/graph.py          The plan → search → synthesize graph
agent/llm.py            Picks the provider from whichever API key is set
agent/search.py         Tavily if TAVILY_API_KEY is set, else DuckDuckGo
agent/logging_setup.py  Per-run logging to logs/<user-id>/<run-id>/
tests/                  Offline tests
feedback-questions.json A sample questionnaire for MaidenRun's feedback form
docker-compose.yml      The entry point MaidenRun runs
Dockerfile
```
