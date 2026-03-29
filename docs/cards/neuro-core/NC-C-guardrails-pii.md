# NC-C — Guardrails + PII-Schutz

**Lane:** Neuro-Core (Lane C)
**Prioritaet:** P1
**Status:** umgesetzt (C1-C3)

## Kontext
AI-Systeme koennen personenbezogene Daten in Ein-/Ausgaben enthalten.
Ohne PII-Erkennung und Prompt-Injection-Schutz ist das System DSGVO-gefaehrdet.

## Loesung
PII Detector mit 8 deutschen Patterns (IBAN, Telefon, Steuer-Nr, etc.).
Reversible und irreversible Maskierung. Prompt-Injection-Erkennung mit 8 Patterns.
Output-Sanitizer maskiert PII in AI-Antworten automatisch.

## Dateien
- `app/services/pii_detector.py` — PII Detection + Masking
- `app/services/guardrails.py` — Input/Output Guardrails
- `app/api/v1/endpoints/neuro_guardrails.py` — REST-API
- `docs/workflows/nc-c-guardrails-pii.md` — Workflow-Doku
