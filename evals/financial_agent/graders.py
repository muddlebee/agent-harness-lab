from __future__ import annotations

from examples.financial_agent.models import RunTrace


def answer_mentions(answer: str, required: tuple[str, ...]) -> bool:
    normalized = answer.lower()
    return all(value.lower() in normalized for value in required)


def trace_used(trace: RunTrace, required: tuple[str, ...]) -> bool:
    names = [event.name for event in trace.events if event.outcome == "ok"]
    return all(name in names for name in required)


def has_no_tool_error(trace: RunTrace) -> bool:
    return all(event.outcome == "ok" for event in trace.events)


def is_efficient(trace: RunTrace, maximum_tool_calls: int) -> bool:
    return len(trace.events) <= maximum_tool_calls
