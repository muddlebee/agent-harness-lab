# Evals and graders: test properties, not one magic trajectory

The offline runner takes a Scenario, builds a sandbox, runs a behavior, then applies small
graders. See evals/financial_agent/runner.py.

M1 defines five scenarios: spending spike, missing merchant data, stale balance, failed budget
write, and a privacy boundary. Each scenario has a user question, failure plan, expected answer
properties, required tools, call budget, and (when relevant) expected final database state.

The spending scenario checks:

~~~text
facts             answer names travel and shopping
valid trajectory  summary and breakdown tools were used
no tool error     failure was not hidden
efficient         no more than four tool calls
~~~

The failed-write scenario adds stronger properties:

~~~text
database state    the old budget row remains ₹1,000
expected error    the timeout appears in the trace
~~~

This avoids an overly brittle rule such as calls must occur in one exact order. Grade
requirements — safe evidence, correct state, cost bounds — not every harmless implementation
detail.

The Inspect task in evals/financial_agent/inspect_task.py runs the actual OpenAI Agents SDK agent
rather than duplicating the reference behavior. Its custom solver creates the sandbox and saves
JSON-safe execution evidence in Inspect's state store. Separate custom scorers read that one
record, so the model is not re-run for every score.
