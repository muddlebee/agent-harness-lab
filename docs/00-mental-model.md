# Mental model: an agent is dropped into a world

An agent eval is not merely a list of prompts and preferred answers. It is a controlled
experiment:

~~~text
task + sandbox state + tools = world with known truth
~~~

The agent sees that world only through tools. The evaluator records three kinds of evidence:

1. Answer — what did the agent tell the user?
2. Trace — what model and tool behavior got it there?
3. State — what actually changed in the sandbox?

For a budget update, the final database row is stronger evidence than a convincing sentence.
This is why the repo keeps a real SQLite-backed service rather than mocking every tool response.
