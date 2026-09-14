"""Resolve the optional live-model provider from environment configuration."""
from __future__ import annotations

import os


def live_model_from_environment():
    """Return an SDK model configured by environment variables, or ``None`` for OpenAI defaults."""
    provider = os.getenv("FINANCIAL_AGENT_PROVIDER", "openai").lower()
    if provider == "openai":
        return os.getenv("OPENAI_MODEL") or None
    if provider != "deepseek":
        raise ValueError(
            "FINANCIAL_AGENT_PROVIDER must be 'openai' or 'deepseek', "
            f"got {provider!r}."
        )

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPSEEK_API_KEY is required when using the DeepSeek provider.")

    from agents import OpenAIChatCompletionsModel
    from openai import AsyncOpenAI

    return OpenAIChatCompletionsModel(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        openai_client=AsyncOpenAI(
            api_key=api_key,
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        ),
        buffer_streamed_tool_calls=True,
    )
