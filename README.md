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

## Intentionally not included yet

No memory vendor, vector database, planner, multi-agent topology, Docker, or a second eval
framework. Those are useful only once the first loop is understandable and measured.
