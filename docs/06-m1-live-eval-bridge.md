# M1: the live eval bridge

The first version of this repository had a deterministic walkthrough and a very small Inspect
text-matching demo. M1 joins the pieces correctly:

~~~text
Inspect sample
  → scenario definition
  → fresh SQLite sandbox and failure plan
  → real OpenAI Agents SDK run
  → answer + tool trace + database snapshot
  → five independent Inspect scorers
~~~

The same Scenario object drives both paths.

| Mode | Purpose | Cost |
|---|---|---|
| Reference runner | Verify scenario and grader design on every PR | Free |
| Inspect live task | Measure the real model and harness | Model usage |

This distinction is deliberate. The reference suite is not proof that an LLM will behave well; it
proves that our world and judge are wired correctly. The live task then measures the actual
agent inside that world.

## OpenRouter configuration

The default local configuration routes `deepseek/deepseek-chat` through OpenRouter's
OpenAI-compatible endpoint. Set `FINANCIAL_AGENT_PROVIDER=openrouter`,
`FINANCIAL_AGENT_MODEL=deepseek/deepseek-chat`, and
`FINANCIAL_AGENT_BASE_URL=https://openrouter.ai/api/v1` in `.env`, then provide the common
`FINANCIAL_AGENT_API_KEY` through the shell or `~/.bashrc`. Run the existing helper with
`./scripts/run-live-eval.sh`; it detects the selected provider and labels the Inspect run as
an OpenRouter model.

## The five M1 worlds

| Scenario | Failure it prevents |
|---|---|
| Spending spike | Incorrect financial explanation |
| Missing merchant | Invented transaction total |
| Stale balance | Presenting stale data as current |
| Budget write timeout | False claim of successful mutation |
| Privacy boundary | Cross-user data access |

## Reading a log

Run the task with an API key, then use the Inspect log viewer. If the answer grader fails, read
the tool trace and state score next:

- Empty trace plus an invented number: model hallucinated instead of using data.
- Error trace plus a success claim: recovery policy is unsafe.
- Correct answer and failed efficiency: tool design or prompting is wasteful.
- Correct-looking answer and failed state: the agent claimed a write that did not happen.

When a live run reveals a failure, turn that exact trace into a permanent Scenario before changing
the harness.
