from evals.financial_agent.inspect_task import financial_agent_eval
from evals.financial_agent.scenarios import SCENARIOS


def test_inspect_task_contains_every_scenario() -> None:
    task = financial_agent_eval()
    assert len(task.dataset) == len(SCENARIOS)
