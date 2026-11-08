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
import math
import os
from dataclasses import dataclass
from typing import Any, Optional

import httpx
from sqlalchemy import text
from sqlalchemy.orm import Session

logger = logging.getLogger("llm.gateway")


@dataclass(frozen=True)
class MeteredCompletion:
    text: str
    input_tokens: int
    output_tokens: int


def _completion(text: str, input_tokens: Any, output_tokens: Any) -> MeteredCompletion:
    if not isinstance(text, str) or any(type(value) is not int or value < 0 for value in (input_tokens, output_tokens)):
        raise LLMUnavailable("Anbieter liefert keinen gueltigen Tokenverbrauch")
    return MeteredCompletion(text, input_tokens, output_tokens)


def _finite_json_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("LLM JSON numbers must be finite")
    return number


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("LLM JSON contains duplicate object keys")
        result[key] = value
    return result


def parse_json_object(response: str) -> dict[str, Any]:
    """Decode a plain JSON object or a complete JSON Markdown code block."""
    cleaned = response.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if len(lines) < 3 or lines[0].strip().lower() not in {"```", "```json"} or lines[-1].strip() != "```":
            raise ValueError("LLM JSON code block is incomplete or unsupported")
        cleaned = "\n".join(lines[1:-1])
    data = json.loads(
        cleaned, parse_float=_finite_json_float, parse_constant=_finite_json_float,
        object_pairs_hook=_unique_json_object,
    )
    if not isinstance(data, dict):
        raise ValueError("LLM response must be a JSON object")
    return data

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

    def complete_metered(self, prompt: str, system: Optional[str] = None,
                         max_tokens: int = 512, timeout: float = 40.0) -> MeteredCompletion:
        """Actual provider usage for reserved jobs; callers own quota settlement.

        Missing usage is an unknown outcome, never guessed or refunded here.
        Existing text-only consumers retain their previous contract.
        """
        if not self.available():
            raise LLMUnavailable("Sprachmodell nicht verfuegbar")
        handlers = {"anthropic": self._anthropic, "openai_compatible": self._openai_compatible, "ollama": self._ollama}
        handler = handlers.get(self.config.provider)
        if handler is None:
            raise LLMUnavailable("Unbekannter Modellanbieter")
        try:
            result = handler(prompt, system, max_tokens, timeout, metered=True)
            if not isinstance(result, MeteredCompletion):
                raise LLMUnavailable("Anbieter-Verbrauch fehlt")
            return result
        except LLMUnavailable:
            raise
        except Exception as error:
            # Do not propagate provider URLs, response bodies or credentials.
            raise LLMUnavailable("Modellaufruf ohne gesicherten Abschluss") from error

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
    def _anthropic(self, prompt: str, system: Optional[str], max_tokens: int, timeout: float, *, metered: bool = False) -> str | MeteredCompletion:
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
        data = resp.json()
        answer = data["content"][0]["text"]
        usage = data.get("usage") or {}
        if metered:
            # Cached input is still consumed context and belongs in the ledger.
            counts = [usage.get("input_tokens"), usage.get("cache_read_input_tokens", 0), usage.get("cache_creation_input_tokens", 0)]
            if any(type(value) is not int or value < 0 for value in counts):
                raise LLMUnavailable("Anbieter-Verbrauch fehlt")
            return _completion(answer, sum(counts), usage.get("output_tokens"))
        return answer

    def _openai_compatible(self, prompt: str, system: Optional[str], max_tokens: int, timeout: float, *, metered: bool = False) -> str | MeteredCompletion:
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
        data = resp.json()
        answer = data["choices"][0]["message"]["content"]
        usage = data.get("usage") or {}
        return _completion(answer, usage.get("prompt_tokens"), usage.get("completion_tokens")) if metered else answer

    def _ollama(self, prompt: str, system: Optional[str], max_tokens: int, timeout: float, *, metered: bool = False) -> str | MeteredCompletion:
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
        data = resp.json()
        answer = data["message"]["content"]
        return _completion(answer, data.get("prompt_eval_count"), data.get("eval_count")) if metered else answer
