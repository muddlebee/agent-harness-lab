# Evals and graders: test properties, not one magic trajectory

The offline runner takes a Scenario, builds a sandbox, runs a behavior, then applies small
graders. See evals/financial_agent/runner.py.

The spending scenario checks:

~~~text
facts             answer names travel and shopping
valid trajectory  summary and breakdown tools were used
no tool error     failure was not hidden
efficient         no more than four tool calls
~~~

The budget scenario adds a stronger property:

~~~text
database state    the budget row is ₹10,000
verified write    update_budget happened before verify_budget
~~~

This avoids an overly brittle rule such as calls must occur in one exact order. Grade
requirements — safe evidence, correct state, cost bounds — not every harmless implementation
detail.

The Inspect task lives in evals/financial_agent/inspect_task.py and establishes the standard
Inspect shape:

~~~text
dataset + solver plan + scorer → saved eval log
~~~

The next iteration can bridge the actual live agent and attach custom state and trace scorers.
