# Sandbox worlds: repeatability, not just security

Every evaluation calls create_sandbox() and seed_maya_spending_spike(). That produces a new
in-memory SQLite database with the same accounts, transactions, budget, and sync timestamp.

~~~text
production agent → FinancialService → real backend
eval agent       → FinancialService → synthetic SQLite
~~~

The tool contract does not change. Only the backend implementation does.

This lets us create precise cases that production data makes hard to test: missing
transactions, stale balances, duplicate ingestion, and forced timeouts. FailurePlan is a
deterministic example: fail set_budget on the first call is a scenario definition, not random
chaos.
