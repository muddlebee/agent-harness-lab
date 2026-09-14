"""Inspect bridge for the real Agents SDK financial agent.

Run with:
  ./scripts/run-deepseek-eval.sh

Inspect stores one JSON-safe execution record per sample. Each scorer then evaluates a different
property of the same answer, trace, and final sandbox state without repeating the model call.
"""
from __future__ import annotations

import os
from datetime import UTC, datetime
from uuid import uuid4

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.log import transcript
from inspect_ai.model import ModelOutput
from inspect_ai.scorer import Score, Target, mean, scorer
from inspect_ai.solver import Generate, Solver, TaskState, solver

from evals.financial_agent.runner import evaluate_live
from evals.financial_agent.scenarios import SCENARIOS, by_id

STORE_KEY = "agent_harness_execution"


def eval_run_id() -> str:
    """Return one stable Langfuse session ID for this Inspect invocation."""
    configured_id = os.getenv("FINANCIAL_AGENT_EVAL_RUN_ID")
    if configured_id:
        return configured_id
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    return f"financial-agent-eval-{timestamp}-{uuid4().hex[:8]}"


@solver
def run_financial_agent() -> Solver:
    """Create a fresh SQLite sandbox and execute the real agent for every Inspect sample."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        scenario = by_id(str(state.metadata["scenario_id"]))
        execution = await evaluate_live(
            scenario, session_id=str(state.metadata["eval_run_id"])
        )
        record = execution.as_dict()
        state.output = ModelOutput(completion=execution.answer)
        state.store.set(STORE_KEY, record)
        transcript().info(record, source="financial_agent")
        state.completed = True
        return state

    return solve


def scorecard(check: str):
    @scorer(metrics=[mean()], name=f"financial_{check}")
    def score_execution():
        async def score(state: TaskState, target: Target) -> Score:
            record = state.store.get(STORE_KEY, {})
            value = bool(record.get("checks", {}).get(check, False))
            return Score(
                value=value,
                answer=str(record.get("answer", "")),
                explanation=f"{check}={value}; scenario={state.metadata['scenario_id']}",
            )

        return score

    return score_execution()


@task
def financial_agent_eval() -> Task:
    run_id = eval_run_id()
    dataset = [
        Sample(
            input=scenario.question,
            target="",
            id=scenario.id,
            metadata={"scenario_id": scenario.id, "eval_run_id": run_id},
        )
        for scenario in SCENARIOS
    ]
    return Task(
        dataset=dataset,
        solver=run_financial_agent(),
        scorer=[
            scorecard("answer"),
            scorecard("trajectory"),
            scorecard("expected_tool_error"),
            scorecard("state"),
            scorecard("efficiency"),
        ],
    )
