from examples.financial_agent.observability import configure_langfuse, langfuse_enabled


def test_langfuse_is_disabled_by_default(monkeypatch) -> None:
    monkeypatch.delenv("LANGFUSE_TRACING_ENABLED", raising=False)
    configure_langfuse.cache_clear()

    assert not langfuse_enabled()
    assert configure_langfuse() is None


def test_langfuse_requires_credentials_when_enabled(monkeypatch) -> None:
    monkeypatch.setenv("LANGFUSE_TRACING_ENABLED", "true")
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_BASE_URL", raising=False)
    configure_langfuse.cache_clear()

    try:
        configure_langfuse()
    except RuntimeError as error:
        assert "LANGFUSE_PUBLIC_KEY" in str(error)
    else:  # pragma: no cover
        raise AssertionError("expected Langfuse configuration to fail without credentials")
    finally:
        configure_langfuse.cache_clear()
