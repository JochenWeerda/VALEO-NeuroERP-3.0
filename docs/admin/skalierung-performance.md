---
title: Skalierung & Performance
type: explanation
audience: [betrieb, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# Skalierung & Performance

Leitlinien für den Betrieb unter Mehrbenutzerlast. Grundlage ist die
Optimierung aus **PERF-MULTIUSER-001**.

## Anwendungsschicht

- **Pure-ASGI-Middleware:** Der HTTP-Middleware-Stack (Prometheus, Correlation,
  Security-Headers, Audit, Bearer-Auth, Request-Logging) läuft als reine
  ASGI-Implementierung. Das senkte den Stack-Overhead von ~82 ms/Request auf
  < 0,3 ms/Request.
- **Schlankes Logging:** Nur langsame Requests (> 1 s) und Fehler werden
  geloggt — weniger I/O unter Last.

## Worker-Skalierung

- Mehrere Uvicorn/Gunicorn-Worker je Instanz nutzen (CPU-gebunden).
- Faustregel als Ausgangspunkt: Worker ≈ Anzahl CPU-Kerne; danach anhand von
  Latenz/Auslastung justieren.
- Horizontal über mehrere Container/Replicas skalieren.

!!! warning "Ressourcenkontention"
    Auf einem ausgelasteten Host bringt mehr Worker keine Verbesserung, sondern
    Verschlechterung (CPU-Oversubscription). Last- und Hostressourcen gemeinsam
    bewerten.

## Datenbank

- SQLAlchemy `QueuePool` ist passend dimensioniert; Pool-Größe an Worker-Zahl und
  DB-Limits ausrichten.
- Langsame Queries über Monitoring identifizieren und indizieren.

## Caching

- Redis für Cache/Rate-Limiting nutzen.
- Frontend: TanStack React Query mit sinnvollem `staleTime` reduziert
  Backend-Last.

## Lasttests

Reproduzierbare Lasttests über `scripts/loadtest/` (httpx-basiert). Ergebnisse
gegen SLOs bewerten, nicht gegen Einzelwerte.
