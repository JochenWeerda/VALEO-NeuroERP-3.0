# NC-A9 - Intent Engine LLM-Fallback

**Lane:** NC-A
**Prioritaet:** P2
**Status:** umgesetzt
**Abhaengigkeit:** NC-A1/A2 (Neuro Intent Engine)

## Kontext

Die Neuro Intent Engine (NC-A1/A2) erkennt Intents ueber Pattern-Matching mit 11 statischen Patterns. Unbekannte Formulierungen fuehren zu `intent=unknown` mit niedriger Confidence. Fuer Stufe-2-Reife braucht die Engine einen LLM-basierten Fallback, der unbekannte Eingaben auf vorhandene Intents mapped.

## Umsetzung

### 1. LLM-Fallback-Pfad in classify()

Wenn Pattern-Matching `unknown` zurueckgibt UND ein LLM-Resolver verfuegbar ist, wird `_classify_with_llm_fallback()` aufgerufen:

- **Injected Resolver** (Primaer): `context["intent_llm_resolver"]` — callable, synchron, gibt Intent-Dict zurueck
- **Service-basiert** (Sekundaer): `context["intent_llm_enabled"] = True` aktiviert den internen `generate_completion()`-Aufruf gegen den AI-Service
- LLM darf nur auf vorhandene INTENT_PATTERNS mappen — keine neuen Intents erfinden
- Confidence wird auf [0.31, 0.95] begrenzt (immer ueber Low-Confidence-Schwelle, nie hoeher als Pattern-Match)

### 2. Prompt-Engineering

`_build_llm_prompt()` erzeugt einen strukturierten Prompt mit:
- Vollstaendige Intent-Liste (intent, category, risk_class, capability) als JSON
- Strikte Antwort-Schema-Vorgabe (JSON mit intent, category, risk_class, confidence_score, etc.)
- System-Message: "Klassifiziere, erfinde keine neuen Intents"
- temperature=0.0, max_tokens=200

### 3. Safety

- Ungueltige LLM-Antworten (unbekannter Intent, broken JSON, Exception) fallen graceful auf `unknown` zurueck
- `_normalize_llm_payload()` akzeptiert Dict oder IntentResult
- `_run_async_llm_completion()` handelt sync/async Event-Loop korrekt

## Dateien

| Datei | Aenderung |
|-------|-----------|
| `app/agents/neuro_intent_engine.py` | `_classify_with_llm_fallback()`, `_resolve_llm_payload()`, `_build_llm_prompt()`, `_normalize_llm_payload()`, `_run_async_llm_completion()` |
| `tests/test_neuro_intent_engine.py` | 3 neue Tests (injected resolver, invalid intent, broken resolver) |
| `tests/test_neuro_pipeline.py` | 1 neuer Test (Pipeline E2E mit LLM-Fallback + dry_run) |

## Verifikation

```bash
pytest tests/test_neuro_intent_engine.py tests/test_neuro_pipeline.py -v --no-cov
```

## Offene Folgearbeit

- Prompt-Pack-Integration: LLM-Prompt aus Prompt-Pack-Registry statt hardcoded
- Feedback-Loop: Confidence-Tracking ueber Confidence Ledger fuer LLM-Fallback-Ergebnisse
- Rate-Limiting / Cost-Guard fuer LLM-Aufrufe
