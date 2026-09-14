import importlib.util
from pathlib import Path

from evals.financial_agent.inspect_task import financial_agent_eval
from evals.financial_agent.scenarios import SCENARIOS


def test_inspect_task_contains_every_scenario() -> None:
    task = financial_agent_eval()
    assert len(task.dataset) == len(SCENARIOS)


def test_inspect_task_assigns_one_langfuse_session_to_all_samples(monkeypatch) -> None:
    monkeypatch.setenv("FINANCIAL_AGENT_EVAL_RUN_ID", "financial-agent-eval-test")

    task = financial_agent_eval()

    assert {
        sample.metadata["eval_run_id"] for sample in task.dataset
    } == {"financial-agent-eval-test"}


def test_inspect_task_loads_as_an_inspect_file() -> None:
    path = Path("evals/financial_agent/inspect_task.py")
    spec = importlib.util.spec_from_file_location("inspect_file_task", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    assert len(module.financial_agent_eval().dataset) == len(SCENARIOS)
