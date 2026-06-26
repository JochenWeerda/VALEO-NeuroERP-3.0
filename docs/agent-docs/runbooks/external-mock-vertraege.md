---
title: External-Mock-Verträge für E2E-Tests
description: Dokumentiert verfügbare /dev/external-mocks/* Endpunkte und Vertragsformat für Playwright-E2E-Tests.
type: reference
audience: [entwickler, qa]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-26
version: 3.0.0
---

# External-Mock-Verträge (EXTERNAL-MOCK-WORKFLOW-001)

Externe Gates (DATEV, ELSTER, TSE, DSFinV-K, Bank/CAMT) sind im Dev/Test-Modus
über `/api/v1/dev/external-mocks/*` erreichbar. Alle Endpunkte antworten mit `simulated: true`.

## Verfügbare Mock-Endpunkte

| Endpunkt | Methode | Beschreibung | Kontrakt |
|---|---|---|---|
| `/dev/external-mocks/datev/export` | POST | DATEV-Export simulieren | `{simulated: true, job_id: "..."}` |
| `/dev/external-mocks/datev/export/{id}` | GET | Export-Status abrufen | `{simulated: true, status: "done"}` |
| `/dev/external-mocks/elster/submit` | POST | ELSTER-Übermittlung simulieren | `{simulated: true, belegnummer: "..."}` |
| `/dev/external-mocks/bank/camt-import` | POST | CAMT-Kontoauszug importieren | `{simulated: true, buchungen: [...]}` |
| `/dev/external-mocks/tse/sign` | POST | TSE-Signatur simulieren | `{simulated: true, signature: "..."}` |
| `/dev/external-mocks/dsfinvk/export` | POST | DSFinV-K-Export simulieren | `{simulated: true, export_id: "..."}` |

## Vertragsformat

```typescript
// Alle Mock-Antworten enthalten:
interface MockResponse {
  simulated: true;          // Pflichtfeld — zeigt Mock-Modus an
  [key: string]: unknown;   // Fachliche Felder je Endpunkt
}
```

## Verwendung in Playwright

```typescript
// @smoke — Mock akzeptiert (503 als Erfolg auch ok):
expect([200, 201, 422, 503]).toContain(res.status())
if (res.status() === 200) {
  const body = await res.json()
  expect(body.simulated).toBe(true)
}

// @critical — kein simulated-Check, kein 503-Fallback:
expect([200, 404, 422]).toContain(res.status())
```

## Aktivierung

Mock-Endpunkte sind nur aktiv wenn `APP_ENV=test` oder `API_DEV_TOKEN` gesetzt.
Produktionsumgebungen lehnen `/dev/*`-Pfade mit 404 ab.

*Slice: EXTERNAL-MOCK-WORKFLOW-001*
