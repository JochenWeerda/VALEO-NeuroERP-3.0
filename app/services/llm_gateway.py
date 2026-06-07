"""Anbieterunabhängiges LLM-Gateway.

Eine einzige Zugriffsschicht für alle LLM-Aufrufe (NeuroAI-Dossier, WhatsApp-
Bestellextraktion, Käufergruppen-Klassifikation). Der Systemadministrator wählt
den Anbieter in den Admin-Einstellungen (`/admin-suite/llm-gateway`); ökonomisch
i. d. R. ein lokaler Dienst (DSGVO/kostenlos), ein günstiger Aggregator oder ein
Cloud-Anbieter:

- ``anthropic``         — api.anthropic.com (Claude)
- ``openai_compatible`` — OpenAI **und** OpenRouter und lokale OpenAI-kompatible
                          Server (Ollama `/v1`, LM Studio, Hermes …) via ``base_url``
- ``ollama``            — lokaler Ollama-Dienst (`/api/chat`)

Konfiguration: Tenant-Settings-Key ``llm_gateway`` (domain_shared.tenants.settings),
mit Env-Defaults. Fällt jeder Anbieter aus (kein Key/Guthaben/Netz), liefert
``complete_or_none`` ``None`` und der Aufrufer nutzt seinen deterministischen
Fallback — der Ablauf funktioniert immer.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Optional

import httpx
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger("llm.gateway")

SETTINGS_KEY = "llm_gateway"
PROVIDERS = ("anthropic", "openai_compatible", "ollama")

_DEFAULT_BASE_URL = {
    "anthropic": "https://api.anthropic.com",
    "openai_compatible": "https://api.openai.com/v1",
    "ollama": "http://localhost:11434",
}
_DEFAULT_MODEL = {
    "anthropic": os.environ.get("ANTHROPIC_MODEL", "claude-opus-4-8"),
    "openai_compatible": os.environ.get("LLM_MODEL", "gpt-4o-mini"),
    "ollama": os.environ.get("OLLAMA_MODEL", "llama3.1"),
}


class LLMUnavailable(RuntimeError):
    """Kein konfigurierter/erreichbarer Anbieter — Aufrufer soll Fallback nutzen."""


@dataclass
class LLMConfig:
    provider: str = "anthropic"
    base_url: str = ""
    model: str = ""
    api_key: str = ""
    temperature: float = 0.2
    enabled: bool = True

    def resolved_base_url(self) -> str:
        return (self.base_url or _DEFAULT_BASE_URL.get(self.provider, "")).rstrip("/")

    def resolved_model(self) -> str:
        return self.model or _DEFAULT_MODEL.get(self.provider, "")


def _env_api_key(provider: str) -> str:
    # Generischer Schlüssel zuerst, dann anbietertypische Env-Variablen.
    if os.environ.get("LLM_API_KEY"):
        return os.environ["LLM_API_KEY"]
    if provider == "anthropic":
        return os.environ.get("ANTHROPIC_API_KEY", "")
    if provider == "openai_compatible":
        return os.environ.get("OPENROUTER_API_KEY") or os.environ.get("OPENAI_API_KEY", "")
    return ""  # ollama braucht i. d. R. keinen Key


def _read_tenant_settings(db: Optional[Session], tenant_id: Optional[str]) -> dict:
    if db is None or not tenant_id:
        return {}
    try:
        raw = db.execute(
            text("SELECT settings FROM domain_shared.tenants WHERE id = :t"), {"t": tenant_id}
        ).scalar()
    except Exception:
        if db is not None:
            db.rollback()
        return {}
    if not raw:
        return {}
    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except Exception:
            return {}
    return raw or {}


def load_config(db: Optional[Session] = None, tenant_id: Optional[str] = None) -> LLMConfig:
    """Lädt die LLM-Konfiguration: Tenant-Settings > Env-Defaults."""
    stored = _read_tenant_settings(db, tenant_id).get(SETTINGS_KEY) or {}
    provider = (stored.get("provider") or os.environ.get("LLM_PROVIDER") or "anthropic").strip()
    if provider not in PROVIDERS:
        provider = "anthropic"
    return LLMConfig(
        provider=provider,
        base_url=(stored.get("base_url") or "").strip(),
        model=(stored.get("model") or "").strip(),
        api_key=(stored.get("api_key") or _env_api_key(provider)).strip(),
        temperature=float(stored.get("temperature", 0.2)),
        enabled=bool(stored.get("enabled", True)),
    )


class LLMGateway:
    def __init__(self, db: Optional[Session] = None, tenant_id: Optional[str] = None,
                 config: Optional[LLMConfig] = None) -> None:
        self.config = config or load_config(db, tenant_id)

    # ── Verfügbarkeit ─────────────────────────────────────────────────────────
    def available(self) -> bool:
        c = self.config
        if not c.enabled:
            return False
        if c.provider == "ollama":
            return bool(c.resolved_base_url())  # lokal, kein Key nötig
        return bool(c.api_key and c.resolved_base_url() and c.resolved_model())

    # ── Hauptzugriff ──────────────────────────────────────────────────────────
    def complete(self, prompt: str, system: Optional[str] = None, max_tokens: int = 1024,
                 timeout: float = 40.0) -> str:
        """Eine Vervollständigung. Wirft LLMUnavailable bei fehlender Config/Fehler."""
        c = self.config
        if not self.available():
            raise LLMUnavailable(f"LLM-Anbieter '{c.provider}' nicht konfiguriert/aktiv")
        try:
            if c.provider == "anthropic":
                return self._anthropic(prompt, system, max_tokens, timeout)
            if c.provider == "openai_compatible":
                return self._openai_compatible(prompt, system, max_tokens, timeout)
            if c.provider == "ollama":
                return self._ollama(prompt, system, max_tokens, timeout)
        except LLMUnavailable:
            raise
        except Exception as exc:  # noqa: BLE001 — jeder Anbieterfehler → einheitlich
            logger.warning("[LLM] %s fehlgeschlagen: %s", c.provider, exc)
            raise LLMUnavailable(str(exc)) from exc
        raise LLMUnavailable(f"Unbekannter Anbieter '{c.provider}'")

    def complete_or_none(self, prompt: str, system: Optional[str] = None,
                         max_tokens: int = 1024) -> Optional[str]:
        try:
            return self.complete(prompt, system, max_tokens)
        except LLMUnavailable:
            return None

    def test(self) -> dict:
        """Konfigurations-/Erreichbarkeitsprobe für die Admin-UI."""
        c = self.config
        if not self.available():
            return {"ok": False, "provider": c.provider, "model": c.resolved_model(),
                    "detail": "Nicht konfiguriert (Key/Base-URL/Modell prüfen)."}
        try:
            out = self.complete("Antworte mit genau dem Wort: OK", max_tokens=8, timeout=20.0)
            return {"ok": True, "provider": c.provider, "model": c.resolved_model(),
                    "detail": (out or "").strip()[:120]}
        except LLMUnavailable as exc:
            return {"ok": False, "provider": c.provider, "model": c.resolved_model(),
                    "detail": f"Probe fehlgeschlagen: {exc}"}

    # ── Anbieter-Implementierungen ────────────────────────────────────────────
    def _anthropic(self, prompt: str, system: Optional[str], max_tokens: int, timeout: float) -> str:
        c = self.config
        body: dict = {"model": c.resolved_model(), "max_tokens": max_tokens,
                      "messages": [{"role": "user", "content": prompt}]}
        if system:
            body["system"] = system
        resp = httpx.post(
            f"{c.resolved_base_url()}/v1/messages",
            headers={"x-api-key": c.api_key, "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            json=body, timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]

    def _openai_compatible(self, prompt: str, system: Optional[str], max_tokens: int, timeout: float) -> str:
        c = self.config
        messages = ([{"role": "system", "content": system}] if system else []) + \
                   [{"role": "user", "content": prompt}]
        headers = {"content-type": "application/json"}
        if c.api_key:
            headers["Authorization"] = f"Bearer {c.api_key}"
        resp = httpx.post(
            f"{c.resolved_base_url()}/chat/completions",
            headers=headers,
            json={"model": c.resolved_model(), "max_tokens": max_tokens,
                  "temperature": c.temperature, "messages": messages},
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def _ollama(self, prompt: str, system: Optional[str], max_tokens: int, timeout: float) -> str:
        c = self.config
        messages = ([{"role": "system", "content": system}] if system else []) + \
                   [{"role": "user", "content": prompt}]
        resp = httpx.post(
            f"{c.resolved_base_url()}/api/chat",
            json={"model": c.resolved_model(), "messages": messages, "stream": False,
                  "options": {"temperature": c.temperature, "num_predict": max_tokens}},
            timeout=timeout,
        )
        resp.raise_for_status()
        return resp.json()["message"]["content"]
