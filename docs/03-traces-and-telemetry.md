# Traces and telemetry: the flight recorder

Telemetry answers **what happened?** Evals answer **was that good?**

RunTrace is intentionally tiny so its role is visible. Each tool wrapper records:

~~~text
tool name + arguments + success/error + result/error
~~~

The OpenAI Agents SDK also provides production-grade tracing for model generations and function
tool calls. This repository's local trace remains useful: it makes evidence available to offline
tests and deterministic graders.

Good outcome with bad behavior is still a signal. A correct answer after twenty repeated calls
may pass factual grading but fail the efficiency grader.
