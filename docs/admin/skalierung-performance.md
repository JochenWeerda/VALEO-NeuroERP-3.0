---
title: Skalierung & Performance
type: explanation
audience: [betrieb, entwickler]
owner: Cursor
status: aktiv
last_reviewed: 2026-09-11
version: 3.1.0
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

### Erntepeak (SPEC-P1-10 / Gap 037)

k6-Skript: `tests/load/harvest-peak.js` mit Profilen:

| PROFILE | Zweck | Dauer / VU |
|---------|-------|------------|
| `full` | Staging-/Peak (Default) | ~20 min, bis 800 VU |
| `local` | docker-compose / localhost | ~2,5 min, 50 VU |
| `smoke` | schneller Smoke | 30 s, 5 VU |

```powershell
# Voraussetzung: Backend (z. B. docker compose -f docker-compose.dev.yml up -d), k6
pwsh scripts/loadtest/run_harvest_peak_local.ps1
pwsh scripts/loadtest/run_harvest_peak_local.ps1 -Profile smoke
```

```bash
./scripts/loadtest/run_harvest_peak_local.sh
./scripts/loadtest/run_harvest_peak_local.sh smoke
```

Summary: `reports/performance/harvest-peak-<profil>-summary.json`.
Details: [tests/load/README.md](../../tests/load/README.md).
Staging-Ausführung bleibt externes Ops-Gate (`load-test.yml`).

### Weitere Scripts

Reproduzierbare httpx-Lasttests unter `scripts/loadtest/` (neben k6).
Ergebnisse gegen SLOs bewerten, nicht gegen Einzelwerte.
