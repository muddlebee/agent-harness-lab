from __future__ import annotations

from typing import Any

from examples.financial_agent.models import RunTrace


def answer_mentions(answer: str, required: tuple[str, ...]) -> bool:
    normalized = answer.lower()
    return all(value.lower() in normalized for value in required)


def trace_used(trace: RunTrace, required: tuple[str, ...]) -> bool:
    names = [event.name for event in trace.events]
    return all(name in names for name in required)


def has_expected_tool_error(trace: RunTrace, expected: bool) -> bool:
    observed = any(event.outcome == "error" for event in trace.events)
    return observed is expected


def is_efficient(trace: RunTrace, maximum_tool_calls: int) -> bool:
    return len(trace.events) <= maximum_tool_calls


def state_matches(snapshot: dict[str, Any], expected_dining_budget_paise: int | None) -> bool:
    return (
        expected_dining_budget_paise is None
        or snapshot["dining_budget_paise"] == expected_dining_budget_paise
    )
