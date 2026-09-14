"""Resolve the optional live-model provider from environment configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class OpenAICompatibleProvider:
    """Default connection values and legacy names for an OpenAI-compatible API."""

    default_model: str
    default_base_url: str
    legacy_api_key_name: str
    legacy_model_name: str
    legacy_base_url_name: str


OPENAI_COMPATIBLE_PROVIDERS = {
    "deepseek": OpenAICompatibleProvider(
        default_model="deepseek-chat",
        default_base_url="https://api.deepseek.com",
        legacy_api_key_name="DEEPSEEK_API_KEY",
        legacy_model_name="DEEPSEEK_MODEL",
        legacy_base_url_name="DEEPSEEK_BASE_URL",
    ),
    "openrouter": OpenAICompatibleProvider(
        default_model="deepseek/deepseek-chat",
        default_base_url="https://openrouter.ai/api/v1",
        legacy_api_key_name="OPENROUTER_API_KEY",
        legacy_model_name="OPENROUTER_MODEL",
        legacy_base_url_name="OPENROUTER_BASE_URL",
    ),
}


def _environment_value(name: str, legacy_name: str, default: str | None = None) -> str | None:
    """Prefer the shared configuration name while accepting the previous provider-specific name."""
    return os.getenv(name) or os.getenv(legacy_name) or default


def live_model_from_environment():
    """Return an SDK model configured by environment variables, or ``None`` for OpenAI defaults."""
    provider = os.getenv("FINANCIAL_AGENT_PROVIDER", "openai").lower()
    if provider == "openai":
        return _environment_value("FINANCIAL_AGENT_MODEL", "OPENAI_MODEL")

    configuration = OPENAI_COMPATIBLE_PROVIDERS.get(provider)
    if configuration is None:
        raise ValueError(
            "FINANCIAL_AGENT_PROVIDER must be 'openai', 'deepseek', or 'openrouter', "
            f"got {provider!r}."
        )

    api_key = _environment_value("FINANCIAL_AGENT_API_KEY", configuration.legacy_api_key_name)
    if not api_key:
        raise RuntimeError(
            "FINANCIAL_AGENT_API_KEY is required when using the "
            f"{provider} provider (or use the legacy {configuration.legacy_api_key_name})."
        )

    model = _environment_value(
        "FINANCIAL_AGENT_MODEL", configuration.legacy_model_name, configuration.default_model
    )
    base_url = _environment_value(
        "FINANCIAL_AGENT_BASE_URL",
        configuration.legacy_base_url_name,
        configuration.default_base_url,
    )

    from agents import OpenAIChatCompletionsModel
    from openai import AsyncOpenAI

    return OpenAIChatCompletionsModel(
        model=model,
        openai_client=AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        ),
        buffer_streamed_tool_calls=True,
    )
