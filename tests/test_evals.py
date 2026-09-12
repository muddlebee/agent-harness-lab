from evals.financial_agent.runner import evaluate
from evals.financial_agent.scenarios import SCENARIOS


def test_offline_eval_suite_passes() -> None:
    results = [evaluate(scenario) for scenario in SCENARIOS]
    assert all(result.passed for result in results), [result.checks for result in results]


def test_timeout_eval_checks_real_sandbox_state_not_just_words() -> None:
    result = evaluate(next(scenario for scenario in SCENARIOS if scenario.kind == "failed_budget_write"))
    assert result.checks["state"]
    assert result.checks["expected_tool_error"]
    assert result.sandbox_state["dining_budget_paise"] == 100_000


def test_privacy_eval_never_calls_a_financial_tool() -> None:
    result = evaluate(next(scenario for scenario in SCENARIOS if scenario.kind == "privacy_boundary"))
    assert result.checks["trajectory"]
    assert result.trace.events == []
