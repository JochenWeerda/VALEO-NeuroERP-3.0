# NC-002 — Interaction State Manager

**Lane:** Neuro-Core
**Prioritaet:** P1 (Architektur-kritisch)
**Status:** umgesetzt

## Kontext
Jeder Interaktionskanal (Chat, WhatsApp, Voice, Email) braucht einen eigenen Dialogzustand, der unabhaengig vom Business State verwaltet wird. Ohne zentrale State Machine entstehen inkonsistente Kanalzustaende und Compliance-Luecken.

## Loesung
Eine kanaluebergreifende State Machine verwaltet den Dialogzustand pro Konversation mit definierten Uebergaengen (new → engaged → qualified → intent_detected → conversion_ready/escalated → closed) und steuert Timing, Tonalitaet und Compliance.

## Dateien
- `app/services/interaction_state_manager.py` — Kern-Service
- `app/api/v1/endpoints/neuro_interactions.py` — REST-API
- `docs/workflows/nc-002-interaction-state-manager.md` — Workflow-Doku
