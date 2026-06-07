"""Unit-Tests für das anbieterunabhängige LLM-Gateway (reine Konfig-/Verfügbarkeitslogik)."""

import pytest

from app.services.llm_gateway import LLMConfig, LLMGateway, PROVIDERS, load_config

pytestmark = pytest.mark.unit


def test_provider_defaults_und_resolver():
    c = LLMConfig(provider="anthropic")
    assert c.resolved_base_url() == "https://api.anthropic.com"
    assert c.resolved_model()  # nicht leer (Default)
    c2 = LLMConfig(provider="ollama")
    assert c2.resolved_base_url() == "http://localhost:11434"


def test_available_anthropic_braucht_key():
    assert LLMGateway(config=LLMConfig(provider="anthropic", api_key="")).available() is False
    assert LLMGateway(config=LLMConfig(provider="anthropic", api_key="sk-x", model="claude-opus-4-8")).available() is True


def test_available_ollama_ohne_key():
    # Ollama ist lokal und braucht keinen Key.
    assert LLMGateway(config=LLMConfig(provider="ollama")).available() is True


def test_disabled_ist_nicht_verfuegbar():
    cfg = LLMConfig(provider="ollama", enabled=False)
    assert LLMGateway(config=cfg).available() is False


def test_complete_or_none_bei_unavailable_ist_none():
    cfg = LLMConfig(provider="anthropic", api_key="")  # kein Key → nicht verfügbar
    assert LLMGateway(config=cfg).complete_or_none("hallo") is None


def test_load_config_unbekannter_provider_faellt_auf_anthropic(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "voodoo")
    cfg = load_config(db=None, tenant_id=None)
    assert cfg.provider == "anthropic"


def test_load_config_ohne_db_nutzt_env(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.1")
    cfg = load_config(db=None, tenant_id=None)
    assert cfg.provider == "ollama"
    assert cfg.provider in PROVIDERS


def test_openai_compatible_key_aus_openrouter_env(monkeypatch):
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "openai_compatible")
    monkeypatch.setenv("OPENROUTER_API_KEY", "or-key")
    cfg = load_config(db=None, tenant_id=None)
    assert cfg.api_key == "or-key"
    assert LLMGateway(config=cfg).available() is True


def test_test_probe_bei_unavailable():
    res = LLMGateway(config=LLMConfig(provider="anthropic", api_key="")).test()
    assert res["ok"] is False
    assert res["provider"] == "anthropic"
