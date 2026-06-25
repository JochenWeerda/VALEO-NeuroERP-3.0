---
title: Monitoring & SLO
type: how-to
audience: [betrieb]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# Monitoring & SLO

Das Backend exportiert Prometheus-Metriken über die Middleware-Schicht. Damit
werden Last, Latenz und Fehler überwacht und SLO-Verletzungen erkannt.

## Metriken

| Metrik (Kategorie) | Aussage |
|---|---|
| HTTP-Requests (Count) | Durchsatz je Pfad/Methode/Status. |
| HTTP-Latenz (Histogram) | Antwortzeiten, Perzentile. |
| In-Progress | Aktuell laufende Requests. |
| SLO-Breaches | Überschreitungen definierter Zielwerte. |

Pfade werden für die Metrik vereinfacht (IDs/UUIDs normalisiert), um
Kardinalität zu begrenzen.

## Health-Checks

- `/healthz` — Liveness ohne Auth (für Loadbalancer/Compose-Healthchecks).
- Weitere fachliche Statusendpunkte je nach Modul.

## Logging

Request-Logging ist bewusst schlank: protokolliert werden **langsame Requests
(> 1 s)** und **Fehler (5xx)**. Korrelations-IDs (`X-Correlation-ID`)
verknüpfen Logeinträge eines Requests.

## SLO-Empfehlung

1. Zielwerte je kritischem Endpoint definieren (z. B. p95-Latenz).
2. Alarmierung bei anhaltenden SLO-Breaches einrichten.
3. Trend statt Einzelausschlag bewerten.

> Hintergrund zur Performance-Optimierung der Middleware:
> [Skalierung & Performance](skalierung-performance.md).
