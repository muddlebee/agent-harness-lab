from __future__ import annotations

import pytest

from examples.financial_agent.agent import SYSTEM_PROMPT, build_agent
from examples.financial_agent.model_provider import live_model_from_environment


def test_openai_provider_uses_configured_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FINANCIAL_AGENT_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_MODEL", "gpt-test")

    assert live_model_from_environment() == "gpt-test"


def test_deepseek_provider_uses_openai_compatible_chat_model(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("FINANCIAL_AGENT_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")
    monkeypatch.setenv("DEEPSEEK_MODEL", "deepseek-chat")
    monkeypatch.setenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    model = live_model_from_environment()

    assert model.model == "deepseek-chat"
    assert str(model._client.base_url) == "https://api.deepseek.com"


def test_deepseek_provider_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FINANCIAL_AGENT_PROVIDER", "deepseek")
    monkeypatch.delenv("DEEPSEEK_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="DEEPSEEK_API_KEY"):
        live_model_from_environment()


def test_agent_builds_with_the_deepseek_model(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("FINANCIAL_AGENT_PROVIDER", "deepseek")
    monkeypatch.setenv("DEEPSEEK_API_KEY", "test-key")

    agent = build_agent()

    assert agent.model.model == "deepseek-chat"
    assert len(agent.tools) == 6


def test_system_prompt_defines_the_sandbox_date() -> None:
    assert "2026-09-01" in SYSTEM_PROMPT
    assert "could not confirm" in SYSTEM_PROMPT
