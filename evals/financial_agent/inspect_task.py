"""Inspect AI integration for the live agent path.

Run with:
  uv run inspect eval evals/financial_agent/inspect_task.py@financial_agent_eval
"""
from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import match
from inspect_ai.solver import generate, system_message


@task
def financial_agent_eval() -> Task:
    dataset = [
        Sample(
            input="In this synthetic world, spending rose because travel added ₹34,500 and shopping added ₹9,500. Why did spending increase?",
            target="travel and shopping",
            id="spending-spike-001",
        )
    ]
    return Task(
        dataset=dataset,
        plan=[
            system_message("Answer only from provided facts. State the two main spending drivers."),
            generate(),
        ],
        scorer=match(ignore_case=True),
    )
