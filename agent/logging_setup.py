import logging
import sys
import uuid
from pathlib import Path

from agent.config import settings


def new_run_logger() -> tuple[str, logging.Logger]:
    """Creates a fresh per-run logger under logs/<user-id>/<run-id>/agent.log."""
    run_id = uuid.uuid4().hex[:8]
    run_dir = Path(settings.log_dir) / settings.user_id / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(f"research_agent.{run_id}")
    logger.setLevel(settings.log_level)
    logger.propagate = False
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    file_handler = logging.FileHandler(run_dir / "agent.log")
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(fmt)
    logger.addHandler(stream_handler)

    return run_id, logger
