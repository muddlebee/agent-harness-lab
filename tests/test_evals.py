from evals.financial_agent.runner import evaluate
from evals.financial_agent.scenarios import SCENARIOS


def test_offline_eval_suite_passes() -> None:
    results = [evaluate(scenario) for scenario in SCENARIOS]
    assert all(result.passed for result in results), [result.checks for result in results]


def test_budget_eval_checks_real_sandbox_state_not_just_words() -> None:
    result = evaluate(next(scenario for scenario in SCENARIOS if scenario.kind == "budget_write"))
    assert result.checks["state"]
    assert result.checks["verified_write"]
