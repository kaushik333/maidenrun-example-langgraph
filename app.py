import gradio as gr

from agent.config import settings
from agent.graph import build_graph
from agent.logging_setup import new_run_logger


def run_research(topic: str) -> str:
    if not topic.strip():
        return "Enter a topic to research."

    run_id, logger = new_run_logger()
    logger.info("run started for topic=%r", topic)
    graph = build_graph(logger)
    try:
        result = graph.invoke({"topic": topic, "queries": [], "findings": [], "report": ""})
    except Exception as exc:
        logger.exception("run failed")
        return f"Something went wrong: {exc}"
    logger.info("run finished")
    return result["report"]


demo = gr.Interface(
    fn=run_research,
    inputs=gr.Textbox(label="Research topic", placeholder="e.g. carbon capture startups in 2025"),
    outputs=gr.Markdown(label="Report"),
    title="Research Agent",
    flagging_mode="never",
)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=settings.app_port)
