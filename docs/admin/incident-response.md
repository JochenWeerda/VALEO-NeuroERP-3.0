---
title: Incident-Response
type: how-to
audience: [betrieb]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# Incident-Response

Leitfaden für den Umgang mit Störungen (Ausfall, Fehlerhäufung,
Performance-Einbruch, Sicherheitsvorfall).

## Sofortmaßnahmen

1. **Erkennen:** Alarm/Monitoring prüfen (Latenz, 5xx, SLO-Breaches).
2. **Eingrenzen:** Betroffene Komponente bestimmen (Backend, DB, NATS, Keycloak,
   Frontend).
3. **Korrelation:** Über `X-Correlation-ID` zusammengehörige Logeinträge finden.
4. **Stabilisieren:** Bei Überlast Worker/Replicas anpassen (siehe
   [Skalierung & Performance](skalierung-performance.md)).

## Eskalation

- Auswirkung und betroffene Mandanten dokumentieren.
- Bei Sicherheits-/Datenschutzvorfall: Compliance einbeziehen
  ([Compliance](../compliance/index.md)).
- Kommunikation an Betroffene gemäß interner Richtlinie.

## Nachbereitung (Post-Mortem)

1. Zeitleiste rekonstruieren (Logs, Metriken, Events).
2. Ursache (Root Cause) benennen.
3. Maßnahmen ableiten und als Slice/Backlog-Eintrag verfolgen.
4. Runbook aktualisieren.

!!! note "Blameless"
    Post-Mortems sind schuldfrei und auf Systemverbesserung ausgerichtet.
