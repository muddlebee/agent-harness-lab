"""The execution boundary shared by offline tests and live model evaluations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from examples.financial_agent.db import create_sandbox, seed_maya_spending_spike
from examples.financial_agent.models import FinancialContext, RunTrace
from examples.financial_agent.service import FailurePlan, FinancialService
from examples.financial_agent.walkthrough import (
    disclose_stale_balance,
    explain_missing_merchant,
    explain_spending_spike,
    handle_failed_budget_write,
    refuse_other_user_data,
)

from .graders import (
    answer_mentions,
    has_expected_tool_error,
    is_efficient,
    state_matches,
    trace_used,
)
from .scenarios import Scenario


@dataclass
class EvaluationResult:
    scenario_id: str
    answer: str
    checks: dict[str, bool]
    trace: RunTrace
    sandbox_state: dict[str, Any]
    mode: str

    @property
    def passed(self) -> bool:
        return all(self.checks.values())

    def as_dict(self) -> dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "answer": self.answer,
            "checks": self.checks,
            "trace": self.trace.as_dict(),
            "sandbox_state": self.sandbox_state,
            "mode": self.mode,
        }


def build_context(scenario: Scenario) -> tuple[FinancialContext, Any]:
    connection = create_sandbox()
    seed_maya_spending_spike(connection)
    context = FinancialContext(
        service=FinancialService(connection, FailurePlan(fail_on_call=dict(scenario.failure_plan))),
        trace=RunTrace(task_id=scenario.id),
    )
    return context, connection


def snapshot(connection: Any) -> dict[str, Any]:
    row = connection.execute(
        "SELECT monthly_limit_paise FROM budgets WHERE user_id = 'maya' AND category = 'dining'"
    ).fetchone()
    return {"dining_budget_paise": None if row is None else int(row["monthly_limit_paise"])}


def grade(
    scenario: Scenario,
    answer: str,
    trace: RunTrace,
    sandbox_state: dict[str, Any],
) -> dict[str, bool]:
    return {
        "answer": answer_mentions(answer, scenario.expected_answer_fragments),
        "trajectory": trace_used(trace, scenario.required_tools),
        "expected_tool_error": has_expected_tool_error(trace, scenario.expected_tool_error),
        "state": state_matches(sandbox_state, scenario.expected_dining_budget_paise),
        "efficiency": is_efficient(trace, scenario.maximum_tool_calls),
    }


def evaluate(scenario: Scenario) -> EvaluationResult:
    """Run reference behavior: deterministic, fast, and suitable for every pull request."""
    context, connection = build_context(scenario)
    if scenario.kind == "spending_spike":
        answer = explain_spending_spike(context, "2026-08")
    elif scenario.kind == "missing_merchant":
        answer = explain_missing_merchant(context, "Uber")
    elif scenario.kind == "stale_balance":
        answer = disclose_stale_balance(context)
    elif scenario.kind == "failed_budget_write":
        answer = handle_failed_budget_write(context, "dining", 10_000)
    elif scenario.kind == "privacy_boundary":
        answer = refuse_other_user_data()
    else:  # pragma: no cover
        raise ValueError(f"unknown scenario kind: {scenario.kind}")

    sandbox_state = snapshot(connection)
    return EvaluationResult(
        scenario_id=scenario.id,
        answer=answer,
        checks=grade(scenario, answer, context.trace, sandbox_state),
        trace=context.trace,
        sandbox_state=sandbox_state,
        mode="reference",
    )


async def evaluate_live(scenario: Scenario) -> EvaluationResult:
    """Run the real SDK agent against the exact same sandbox and graders.

    This is intentionally not part of the default test suite: it calls a configured model.
    """
    from agents import Runner

    from examples.financial_agent.agent import build_agent

    context, connection = build_context(scenario)
    run = await Runner.run(build_agent(), scenario.question, context=context, max_turns=8)
    answer = str(run.final_output)
    sandbox_state = snapshot(connection)
    return EvaluationResult(
        scenario_id=scenario.id,
        answer=answer,
        checks=grade(scenario, answer, context.trace, sandbox_state),
        trace=context.trace,
        sandbox_state=sandbox_state,
        mode="live",
    )
