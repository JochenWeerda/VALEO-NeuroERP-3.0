# NC-004 — Consent Engine

**Lane:** Neuro-Core
**Prioritaet:** P1 (Architektur-kritisch)
**Status:** umgesetzt

## Kontext
DSGVO Art. 6 und 7 verlangen expliziten, nachweisbaren Consent fuer jede Datenverarbeitung und Kanalnutzung. Ohne zentrale Consent-Verwaltung drohen Bussgelder und Compliance-Verstoesse.

## Loesung
Eine zentrale Consent Engine verwaltet den vollstaendigen Einwilligungs-Lifecycle (Anfrage, Erteilung, Widerruf) mit Audit-Trail und prueft vor jeder Verarbeitung den aktuellen Consent-Status.

## Dateien
- `app/services/consent_engine.py` — Kern-Service
- `app/api/v1/endpoints/neuro_consent.py` — REST-API
- `docs/workflows/nc-004-consent-engine.md` — Workflow-Doku
