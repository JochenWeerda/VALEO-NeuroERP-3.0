---
title: MCP-Rechnungsvorschlag ohne Buchung
type: reference
audience: [agent, entwickler, qa]
owner: Cursor
status: aktiv
last_reviewed: 2026-09-29
description: sales.invoice.propose speichert einen ausstehenden Vorschlag und bucht keine Rechnung.
---

# Rechnungsvorschlag über MCP

`POST /api/v1/mcp/tools/call` mit verifiziertem Token. Der Token braucht `sub`,
`tenant_id` und Scope `sales:write`. Ein abweichender `X-Tenant-ID` wird abgewiesen.

```json
{
  "tool_name": "sales.invoice.propose",
  "parameters": {
    "lieferschein_nr": "LIEFERSCHEINNUMMER",
    "rechnungsdatum": "2026-09-29"
  },
  "mode": "propose",
  "idempotency_key": "STABILER-SCHLUESSEL"
}
```

Ohne Modus gilt `dryRun`. `validate` und `dryRun` lesen den Lieferschein des
Token-Mandanten und geben Netto, Steuer und Positionszahl zurück. Sie speichern
nichts. Der Lieferschein muss `posted`, `printed` oder `gebucht` sein und
gespeicherte Summen haben.

`propose` verlangt einen Wiederholungsschlüssel und schreibt einen Datensatz in
`agent_proposals` (`action_type=rechnung_vorschlag`, `approval_status=pending`,
Risiko hoch) plus Audit und Replay-Journal. `entwurf_id` ist die Proposal-ID,
keine Rechnungsnummer. `posted` ist falsch.

`execute` antwortet mit HTTP 501. Ein Feld `approval_granted` ist kein
erlaubter Parameter und wird mit HTTP 422 abgewiesen. Die Rechnung entsteht
weiter nur über den menschlichen Lieferschein-Pfad.

## Nachweis

`python -m pytest tests/test_mcp_execution.py --noconftest -q --override-ini addopts=''`

Der Vertrag prüft Statuscodes, dass `dryRun` nicht committet, dass `execute`
die Datenbank nicht anfasst und dass `propose` nur `agent_proposals` schreibt.
Eine PostgreSQL-Runde für diesen Vorschlag ist damit nicht ersetzt.

## Grenzen

Weitere Katalog-Tools bleiben ohne Adapter. Der AI-Dienst wird durch diesen
Pfad nicht zum Client. Buchen, SEPA und Masken-Feldschreiben bleiben zu.
