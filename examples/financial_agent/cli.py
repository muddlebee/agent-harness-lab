from __future__ import annotations

import argparse

from .agent import build_agent
from .db import create_sandbox, seed_maya_spending_spike
from .models import FinancialContext, RunTrace
from .service import FinancialService
from .walkthrough import explain_spending_spike


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the financial agent example.")
    parser.add_argument("question", nargs="?", default="Why did I spend so much last month?")
    parser.add_argument("--live", action="store_true", help="Use OpenAI Agents SDK instead of offline walkthrough.")
    args = parser.parse_args()

    connection = create_sandbox()
    seed_maya_spending_spike(connection)
    context = FinancialContext(service=FinancialService(connection), trace=RunTrace(task_id="manual-run"))
    if args.live:
        from agents import Runner

        output = Runner.run_sync(build_agent(), args.question, context=context).final_output
    else:
        output = explain_spending_spike(context, "2026-08")
    print(output)
    print("\nTrace:")
    for event in context.trace.events:
        print(f"- {event.name}: {event.outcome}")


if __name__ == "__main__":
    main()
