"""
Structured logging setup.

Every log line includes contextual fields (tenant_id, session_id, node_name)
where relevant, so logs are actually greppable/traceable per-conversation in
production — critical for debugging a multi-tenant async graph where many
conversations are in flight concurrently.
"""
import logging
import sys
from typing import Any

from app.config.settings import get_settings


class ContextualLogger(logging.LoggerAdapter):
    """
    LoggerAdapter that merges a base context (e.g. tenant_id, session_id)
    into every log call, and allows per-call extra context on top of it.

    Usage:
        log = get_logger(__name__, tenant_id="t1", session_id="s1")
        log.info("Dispatching reply", extra={"reply_type": "image"})
    """

    def process(self, msg: str, kwargs: dict[str, Any]) -> tuple[str, dict[str, Any]]:
        extra = kwargs.get("extra", {})
        merged_context = {**self.extra, **extra}
        context_str = " ".join(f"{k}={v}" for k, v in merged_context.items() if v is not None)
        kwargs["extra"] = merged_context
        return (f"{msg} | {context_str}" if context_str else msg), kwargs


def _configure_root_logger() -> None:
    settings = get_settings()
    root = logging.getLogger()
    if root.handlers:
        # Already configured (e.g. re-imported in tests) — avoid duplicate handlers.
        return

    root.setLevel(settings.log_level.upper())
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    root.addHandler(handler)


def get_logger(name: str, **context: Any) -> ContextualLogger:
    """
    Returns a logger scoped to `name` (typically __name__), optionally
    pre-bound with context fields that will appear on every log line.
    """
    _configure_root_logger()
    base_logger = logging.getLogger(name)
    return ContextualLogger(base_logger, context)
