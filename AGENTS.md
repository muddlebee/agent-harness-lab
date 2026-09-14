# Agent Harness Lab instructions

## Working agreement

- Keep changes small, explicit, and reversible; preserve the deterministic offline path.
- Prefer the existing agent → tools → SQLite sandbox → trace → graders → Inspect eval loop over new frameworks or abstractions.
- Use a fresh sandbox for each evaluation scenario. Do not weaken deterministic graders to accommodate a model failure; diagnose the trace first.
- Treat live model calls as opt-in: they cost money and can be nondeterministic. Use the offline suite by default.

## Commands and validation

- Install development and eval dependencies with `uv sync --extra dev --extra evals`.
- Run `uv run pytest -q` and `uv run ruff check .` after code changes.
- Run live DeepSeek evaluations through `./scripts/run-deepseek-eval.sh`; use `INSPECT_SAMPLE_ID` for a focused paid smoke test.
- Review Inspect logs and Langfuse traces when a live evaluation fails before changing prompts, tools, or graders.

## Credentials and observability

- Never commit `.env`, API keys, tokens, or generated evaluation logs.
- Keep Langfuse content capture disabled for real financial data. `LANGFUSE_CAPTURE_CONTENT=true` is only appropriate for synthetic, approved debugging runs.
- Use a new Langfuse session for each evaluation invocation; reuse `FINANCIAL_AGENT_EVAL_RUN_ID` only when intentionally appending traces to the same experiment.

## Documentation

- Update `README.md` for changed setup or run commands.
- Update the relevant file under `docs/` for changed architecture, telemetry, or evaluation behavior.
- Record proposed learning experiments in `TODO.md` rather than silently expanding scope.
