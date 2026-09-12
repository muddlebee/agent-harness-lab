# The experiment loop: turn failures into permanent knowledge

The practical loop is:

~~~text
observe failure → reproduce as scenario → change harness → rerun suite → keep regression test
~~~

Example: an agent says a budget update succeeded after a timeout.

1. Add a scenario using FailurePlan(fail_on_call={"set_budget": 1}).
2. Require either a verified successful retry or a transparent failure response.
3. Change the tool or retry policy.
4. Run the same scenario across candidates.
5. Keep it forever after the fix passes.

That is why traces, sandbox state, and evals belong together. A trace diagnoses the miss; a
sandbox makes it reproducible; a grader prevents the same miss from returning.
