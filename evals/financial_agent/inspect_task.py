"""Inspect bridge for the real OpenAI Agents SDK financial agent.

Run with:
  OPENAI_API_KEY=... uv run inspect eval evals/financial_agent/inspect_task.py@financial_agent_eval

Inspect stores one JSON-safe execution record per sample. Each scorer then evaluates a different
property of the same answer, trace, and final sandbox state without repeating the model call.
"""
from __future__ import annotations

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.log import transcript
from inspect_ai.model import ModelOutput
from inspect_ai.scorer import Score, Target, mean, scorer
from inspect_ai.solver import Generate, Solver, TaskState, solver

from .runner import evaluate_live
from .scenarios import SCENARIOS, by_id

STORE_KEY = "agent_harness_execution"


@solver
def run_openai_financial_agent() -> Solver:
    """Create a fresh SQLite sandbox and execute the real agent for every Inspect sample."""

    async def solve(state: TaskState, generate: Generate) -> TaskState:
        scenario = by_id(str(state.metadata["scenario_id"]))
        execution = await evaluate_live(scenario)
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
    dataset = [
        Sample(
            input=scenario.question,
            target="",
            id=scenario.id,
            metadata={"scenario_id": scenario.id},
        )
        for scenario in SCENARIOS
    ]
    return Task(
        dataset=dataset,
        solver=run_openai_financial_agent(),
        scorer=[
            scorecard("answer"),
            scorecard("trajectory"),
            scorecard("expected_tool_error"),
            scorecard("state"),
            scorecard("efficiency"),
        ],
    )
