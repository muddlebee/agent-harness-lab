# Learning backlog

## Next: investigate the budget timeout

- [ ] Open the `budget-write-timeout-001` trace in Langfuse.
- [ ] Identify the DeepSeek tool-call and response path that missed the safe timeout behavior.
- [ ] Improve the prompt, tool contract, or grader only where the trace identifies a real gap.
- [ ] Re-run the five-scenario session and compare the scores.

## Model and evaluation experiments

- [ ] Compare DeepSeek and OpenAI on the same scenarios: pass rate, tool calls, tokens, latency, and failures.
- [ ] Add adversarial scenarios: ambiguous merchants, duplicate transactions, malformed months, invalid budgets, and prompt-injection text in transaction descriptions.
- [ ] Add regression runs: fast offline tests for every commit, with live model evaluation as an opt-in cost-controlled check.

## Reliability and safety

- [ ] Define a retry policy for transient read failures.
- [ ] Require explicit verification before reporting a financial write as successful.
- [ ] Add tests for uncertain-write and partial-failure behavior.

## Langfuse observability

- [ ] Add stable trace tags such as provider, feature, and evaluation mode.
- [ ] Create a Langfuse dashboard for grader scores, latency, token usage, and tool-call counts.
- [ ] Keep `LANGFUSE_CAPTURE_CONTENT=true` only for synthetic learning runs; disable it for real financial data.
