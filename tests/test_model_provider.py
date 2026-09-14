from __future__ import annotations

import pytest

from examples.financial_agent.agent import SYSTEM_PROMPT, build_agent
from examples.financial_agent.model_provider import live_model_from_environment


def test_openai_provider_uses_configured_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FINANCIAL_AGENT_PROVIDER", "openai")
    monkeypatch.delenv("FINANCIAL_AGENT_MODEL", raising=False)
    monkeypatch.setenv("OPENAI_MODEL", "gpt-test")

    assert live_model_from_environment() == "gpt-test"


def test_deepseek_provider_uses_openai_compatible_chat_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FINANCIAL_AGENT_PROVIDER", "deepseek")
    monkeypatch.setenv("FINANCIAL_AGENT_API_KEY", "test-key")
    monkeypatch.setenv("FINANCIAL_AGENT_MODEL", "deepseek-chat")
    monkeypatch.setenv("FINANCIAL_AGENT_BASE_URL", "https://api.deepseek.com")

    model = live_model_from_environment()

    assert model.model == "deepseek-chat"
    assert str(model._client.base_url) == "https://api.deepseek.com"


def test_deepseek_provider_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FINANCIAL_AGENT_PROVIDER", "deepseek")
    monkeypatch.delenv("FINANCIAL_AGENT_API_KEY", raising=False)
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="FINANCIAL_AGENT_API_KEY"):
        live_model_from_environment()


def test_openrouter_provider_uses_deepseek_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FINANCIAL_AGENT_PROVIDER", "openrouter")
    monkeypatch.setenv("FINANCIAL_AGENT_API_KEY", "test-key")
    monkeypatch.setenv("FINANCIAL_AGENT_MODEL", "deepseek/deepseek-chat")
    monkeypatch.setenv("FINANCIAL_AGENT_BASE_URL", "https://openrouter.ai/api/v1")

    model = live_model_from_environment()

    assert model.model == "deepseek/deepseek-chat"
    assert str(model._client.base_url).rstrip("/") == "https://openrouter.ai/api/v1"


def test_openrouter_provider_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FINANCIAL_AGENT_PROVIDER", "openrouter")
    monkeypatch.delenv("FINANCIAL_AGENT_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="FINANCIAL_AGENT_API_KEY"):
        live_model_from_environment()


def test_provider_specific_environment_variables_remain_supported(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FINANCIAL_AGENT_PROVIDER", "openrouter")
    monkeypatch.delenv("FINANCIAL_AGENT_API_KEY", raising=False)
    monkeypatch.delenv("FINANCIAL_AGENT_MODEL", raising=False)
    monkeypatch.delenv("FINANCIAL_AGENT_BASE_URL", raising=False)
    monkeypatch.setenv("OPENROUTER_API_KEY", "legacy-test-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "deepseek/deepseek-v3.2")
    monkeypatch.setenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

    model = live_model_from_environment()

    assert model.model == "deepseek/deepseek-v3.2"


def test_agent_builds_with_the_deepseek_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FINANCIAL_AGENT_PROVIDER", "deepseek")
    monkeypatch.setenv("FINANCIAL_AGENT_API_KEY", "test-key")
    monkeypatch.delenv("FINANCIAL_AGENT_MODEL", raising=False)

    agent = build_agent()

    assert agent.model.model == "deepseek-chat"
    assert len(agent.tools) == 6


def test_system_prompt_defines_the_sandbox_date() -> None:
    assert "2026-09-01" in SYSTEM_PROMPT
    assert "could not confirm" in SYSTEM_PROMPT
