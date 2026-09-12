from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Scenario:
    id: str
    question: str
    kind: str
    expected_drivers: tuple[str, ...] = ()
    expected_budget_paise: int | None = None


SCENARIOS = [
    Scenario(
        id="spending-spike-001",
        question="Why did I spend so much last month?",
        kind="spending_spike",
        expected_drivers=("travel", "shopping"),
    ),
    Scenario(
        id="budget-write-001",
        question="Set my dining budget to ₹10,000.",
        kind="budget_write",
        expected_budget_paise=1_000_000,
    ),
]
