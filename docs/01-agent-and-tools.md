# Agent and tools: make truth executable

Maya asks, “Why did I spend so much last month?” The agent should not receive thousands of raw
transactions and attempt arithmetic in prose. It gets narrow tools:

~~~text
get_monthly_spending(month)
get_category_breakdown(month)
update_budget(category, monthly_limit_paise)
verify_budget(category)
~~~

The LLM chooses a useful sequence and explains the result. Code owns arithmetic, data access,
and writes.

The key security choice is equally simple: there is no model-controlled user id argument. The
service gets the authenticated identity from FinancialContext. A model can ask for Bob's
finances; it cannot create a valid tool call that switches to Bob.

Run the deterministic walkthrough:

~~~bash
uv run financial-agent
~~~

Then inspect the printed trace. The answer is only one output; tool calls are another.
