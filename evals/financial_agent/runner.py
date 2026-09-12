"""Offline evaluator used by pytest and documentation.

Inspect AI is the canonical runner for live LLM evaluations; this mirrors the same scenario,
sandbox, trace, and scoring vocabulary without requiring model access.
"""
from __future__ import annotations

from dataclasses import dataclass

from examples.financial_agent.db import create_sandbox, seed_maya_spending_spike
from examples.financial_agent.models import FinancialContext, RunTrace
from examples.financial_agent.service import FinancialService
from examples.financial_agent.walkthrough import explain_spending_spike, set_and_verify_budget

from .graders import answer_mentions, has_no_tool_error, is_efficient, trace_used
from .scenarios import Scenario


@dataclass
class EvaluationResult:
    scenario_id: str
    answer: str
    checks: dict[str, bool]
    trace: RunTrace

    @property
    def passed(self) -> bool:
        return all(self.checks.values())


def evaluate(scenario: Scenario) -> EvaluationResult:
    connection = create_sandbox()
    seed_maya_spending_spike(connection)
    trace = RunTrace(task_id=scenario.id)
    context = FinancialContext(service=FinancialService(connection), trace=trace)

    if scenario.kind == "spending_spike":
        answer = explain_spending_spike(context, "2026-08")
        checks = {
            "facts": answer_mentions(answer, scenario.expected_drivers),
            "valid_trajectory": trace_used(
                trace, ("get_monthly_spending", "get_category_breakdown")
            ),
            "no_tool_error": has_no_tool_error(trace),
            "efficient": is_efficient(trace, 4),
        }
    elif scenario.kind == "budget_write":
        answer = set_and_verify_budget(context, "dining", 10_000)
        persisted = connection.execute(
            "SELECT monthly_limit_paise FROM budgets WHERE user_id = 'maya' AND category = 'dining'"
        ).fetchone()[0]
        checks = {
            "state": persisted == scenario.expected_budget_paise,
            "verified_write": trace_used(trace, ("update_budget", "verify_budget")),
            "no_tool_error": has_no_tool_error(trace),
            "efficient": is_efficient(trace, 2),
        }
    else:  # pragma: no cover
        raise ValueError(f"unknown scenario kind: {scenario.kind}")
    return EvaluationResult(scenario.id, answer, checks, trace)
