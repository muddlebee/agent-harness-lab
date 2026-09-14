"""Optional Langfuse tracing for live financial-agent runs."""
from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from evals.financial_agent.scenarios import Scenario


def langfuse_enabled() -> bool:
    """Return whether the user explicitly opted into remote Langfuse tracing."""
    return os.getenv("LANGFUSE_TRACING_ENABLED", "false").lower() == "true"


def _capture_content() -> bool:
    return os.getenv("LANGFUSE_CAPTURE_CONTENT", "false").lower() == "true"


@lru_cache(maxsize=1)
def configure_langfuse() -> Any | None:
    """Install the Agents SDK instrumentor and return a configured Langfuse client.

    Tracing is off unless explicitly enabled. This prevents financial inputs and outputs from
    leaving the process accidentally.
    """
    if not langfuse_enabled():
        return None

    missing = [
        name
        for name in ("LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY", "LANGFUSE_BASE_URL")
        if not os.getenv(name)
    ]
    if missing:
        raise RuntimeError(f"Langfuse tracing is enabled but missing: {', '.join(missing)}.")

    try:
        from langfuse import get_client
        from openinference.instrumentation import TraceConfig
        from openinference.instrumentation.openai_agents import OpenAIAgentsInstrumentor
    except ImportError as error:  # pragma: no cover
        raise RuntimeError(
            "Install observability dependencies with: uv sync --extra observability"
        ) from error

    instrumentor = OpenAIAgentsInstrumentor()
    if not instrumentor.is_instrumented_by_opentelemetry:
        instrumentor.instrument(
            config=TraceConfig(
                hide_inputs=not _capture_content(),
                hide_outputs=not _capture_content(),
            )
        )

    client = get_client()
    if not client.auth_check():
        raise RuntimeError("Langfuse authentication failed. Check your keys and base URL.")
    return client


@contextmanager
def observe_live_evaluation(scenario: Scenario) -> Iterator[Any | None]:
    """Create a privacy-preserving root span around one live evaluation scenario."""
    client = configure_langfuse()
    if client is None:
        yield None
        return

    input_data: dict[str, str] = {"scenario_id": scenario.id}
    if _capture_content():
        input_data["question"] = scenario.question

    with client.start_as_current_observation(
        as_type="agent",
        name="financial-agent.live-eval",
        input=input_data,
        metadata={"scenario_id": scenario.id, "scenario_kind": scenario.kind},
    ) as observation:
        yield observation

    client.flush()
