# Agent Harness Lab

A small, docs-first reference project for learning how to make an AI agent reliable:

~~~text
agent + tools + sandbox + trace + graders + eval suite + experiment loop
~~~

The running example is a financial assistant for a synthetic user, Maya. It keeps one
canonical path:

~~~text
OpenAI Agents SDK → financial tools → SQLite sandbox → traces → Inspect AI → scorers
~~~

The financial backend and deterministic tests work without an API key. The live agent is an
optional layer, so you can learn the harness before spending tokens.

## Start here

~~~bash
uv sync --extra dev --extra evals
uv run pytest
uv run financial-agent "Why did I spend so much last month?"
~~~

The last command uses a deterministic walkthrough by default. To run the live agent, set
OPENAI_API_KEY and pass --live.

~~~bash
cp .env.example .env
uv run financial-agent --live "Why did I spend so much last month?"
~~~

Run the Inspect task (requires the evals extra and a configured OpenAI model):

~~~bash
uv run inspect eval evals/financial_agent/inspect_task.py@financial_agent_eval
~~~

That command is intentionally a live, paid run. It creates a fresh SQLite sandbox for each
scenario, calls the actual OpenAI Agents SDK agent, and saves a log with separate answer,
trajectory, expected-error, database-state, and efficiency scores. Regular pull requests run the
offline reference suite only.

### Run the OpenRouter DeepSeek baseline

The local `.env` selects OpenRouter's `deepseek/deepseek-chat` model at
`https://openrouter.ai/api/v1`; it never contains a key. Create an API key in the
[OpenRouter dashboard](https://openrouter.ai/settings/keys), then export the provider-neutral
`FINANCIAL_AGENT_API_KEY` in your current shell or `~/.bashrc`. The helper runs samples one at a
time for readable traces and saves Inspect logs under `logs/`.

~~~bash
./scripts/run-live-eval.sh
INSPECT_SAMPLE_ID=spending-spike-001 ./scripts/run-live-eval.sh
uv run inspect view start --log-dir logs
~~~

Inspect's selected model labels the evaluation. The actual agent model is configured by
`FINANCIAL_AGENT_PROVIDER`, `FINANCIAL_AGENT_MODEL`, and `FINANCIAL_AGENT_BASE_URL` in `.env`.

To keep using DeepSeek directly, set `FINANCIAL_AGENT_PROVIDER=deepseek` and configure
the same three `FINANCIAL_AGENT_*` variables with `deepseek-chat` and
`https://api.deepseek.com`.

### Trace live runs in Langfuse

Install the optional observability dependencies, then add Langfuse credentials to the ignored
local `.env` file (the runner also supports environment variables or `~/.bashrc` as a fallback):

~~~bash
uv sync --extra observability
~~~

Set the following in `.env` before running a synthetic scenario:

~~~bash
LANGFUSE_TRACING_ENABLED=true
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
LANGFUSE_CAPTURE_CONTENT=true
~~~

The agent, model calls, tool calls, and one `financial-agent.live-eval` root span appear in
Langfuse. The root span includes the scenario ID and five deterministic grader scores. Content
capture is off by default because a real financial workload can contain sensitive data.

Every `run-live-eval.sh` invocation generates one Langfuse session ID. Each scenario remains
an independent trace, while all scenarios from that Inspect invocation appear together in the
session replay. The command prints the session ID; use it in Langfuse's Sessions view to compare
the traces. Run the full five-scenario session with:

~~~bash
./scripts/run-live-eval.sh
~~~

Set `FINANCIAL_AGENT_EVAL_RUN_ID` only when intentionally appending traces to an existing
session.

## The mental model

~~~mermaid
flowchart TD
  U[User task] --> A[Agent harness]
  A --> T[Tools]
  T --> S[Sandbox world]
  A --> R[Trace]
  S --> G[State grader]
  R --> G
  G --> M[Scores and diagnosis]
  M --> H[Harness change]
~~~

| Layer | In this repo | Why it exists |
|---|---|---|
| Agent | OpenAI Agents SDK example | Chooses tools and explains results |
| Tools | narrow financial functions | Put facts and arithmetic in code |
| Sandbox | fresh in-memory SQLite | Gives every eval a controlled world |
| Trace | local RunTrace records | Captures behavior, not just the answer |
| Graders | deterministic Python | Checks facts, state, safety, and cost |
| Eval runner | Inspect AI task | Runs scenarios repeatedly and logs results |

## Learning path

1. [Mental model](docs/00-mental-model.md)
2. [The financial agent and its tools](docs/01-agent-and-tools.md)
3. [Sandbox worlds](docs/02-sandbox-worlds.md)
4. [Traces and telemetry](docs/03-traces-and-telemetry.md)
5. [Evals and graders](docs/04-evals-and-graders.md)
6. [The experiment loop](docs/05-experiment-loop.md)
7. [M1: live eval bridge](docs/06-m1-live-eval-bridge.md)

## Intentionally not included yet

No memory vendor, vector database, planner, multi-agent topology, Docker, or a second eval
framework. Those are useful only once the first loop is understandable and measured.
