# NC-002 — Interaction State Manager

## Zweck
Verwaltet den Kanal-/Dialogzustand fuer alle Interaktionskanaele (Chat, WhatsApp, Voice, Email).
Getrennt vom Business State — steuert Timing, Tonalitaet und Compliance pro Konversation.

## Mermaid

```mermaid
stateDiagram-v2
    [*] --> new
    new --> engaged: Erste Nachricht
    engaged --> qualified: Identifiziert
    qualified --> intent_detected: Intent erkannt
    intent_detected --> conversion_ready: Angebot/Aktion bereit
    intent_detected --> escalated: Eskalation noetig
    conversion_ready --> closed: Abschluss
    escalated --> closed: Geloest
    engaged --> closed: Timeout
    qualified --> closed: Timeout
```

## API

- `POST /api/v1/neuro/interactions` — Neue Interaktion starten
- `PUT /api/v1/neuro/interactions/{id}/transition` — Zustandsuebergang
- `GET /api/v1/neuro/interactions/{id}` — Aktuellen Zustand abrufen
- `GET /api/v1/neuro/interactions` — Aktive Interaktionen listen

## Status

| Slice | Beschreibung | Status |
|-------|-------------|--------|
| NC-002-A | State Machine + API | umgesetzt |
| NC-002-B | Channel-Integration | umgesetzt |
