---
title: Ausfuehrbarer CRM-Kontaktadapter
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-21
description: Vertrag, Persistenznachweis und Grenzen des ersten authentifizierten MCP-Schreibadapters.
---

# CRM-Kontakt schreiben

`POST /api/v1/mcp/tools/call` mit verifiziertem OIDC-Bearer-Token.
Der Token muss `sub`, `tenant_id` und Scope `crm:write` enthalten.
Ein optionaler `X-Tenant-ID` muss exakt dem Token entsprechen.

```json
{
  "tool_name": "crm.contact.log",
  "parameters": {
    "kunden_nr": "KUNDENNUMMER",
    "kanal": "telefon",
    "ergebnis": "Kontaktinhalt",
    "wiedervorlage_datum": null
  },
  "mode": "execute",
  "idempotency_key": "STABILER-SCHLUESSEL-DIESES-AUFTRAGS"
}
```

Ohne Modus gilt `dryRun`. `validate`, `dryRun` und `propose` validieren
Parameter und Kundenberechtigung ohne Kontaktanlage. `execute` verlangt einen
Wiederholungsschluessel. Dieselbe Anfrage liefert bei Wiederholung dieselbe
Kontakt-ID; veraenderte Parameter oder ein anderer Akteur mit demselben
Schluessel liefern 409. Die Serialisierung erfolgt per PostgreSQL-Transaktionslock,
das Journal hat einen Primaerschluessel aus Mandant, Tool und Schluessel.

Der vorhandene `CrmKontaktService` schreibt denselben Kontakt wie die UI.
Sein interner Commit liegt innerhalb eines Savepoints. Erst der gemeinsame
Commit speichert Kontakt, Audit und Replay-Journal. Ein Audit-/Journalfehler
rollt die Kontaktanlage zurueck. Die Ergebnisantwort enthaelt `kontakt_id`,
`erfasst_am`, `auditEntryId`, `success`, `mode` und `replayed`.

Der Legacy-Kundenstamm hat keine Tenant-Spalte. Die Berechtigung wird deshalb
ueber `kunden.business_partner_id -> domain_crm.business_partners.tenant_id`
geprueft. Nicht zugeordnete Altkunden werden abgewiesen, nicht still einem
Default-Mandanten zugerechnet. Fachliche Nachzuordnung solcher Altkunden ist
gegebenenfalls weiterhin erforderlich.

## Verifikation

- 41 Tests: `test_mcp_execution.py`, `test_mcp_tool_registry.py`,
  `test_mask_action_atomic.py`, jeweils `--noconftest --override-ini addopts=''`.
- HTTP-Negativtests fuer fehlenden Bearer, falschen Tenant, fehlende Claims/
  Scopes, fremde Kunden, fehlenden Replay-Key und eingeschleuste Identitaets-
  oder Freigabefelder. Vorschau schreibt nicht.
- PostgreSQL: synthetischer Geschaeftspartner und Kunde; reale Kontaktanlage,
  Audit-ID, Replay ohne zweiten Kontakt, 409 bei geaendertem Inhalt und Rollback
  der Kontaktanlage bei erzwungenem Auditfehler. Alle Testdaten zurueckgerollt.
  Lokales Nachweisskript: `artifacts/test_mcp_execution_postgres.py`.
- `mcp_tool_executions_20260921` lokal erfolgreich migriert.
- Architektur-Validate und Drift gruen nach Nachtrag der fuenf bestehenden
  fehlenden Modulzuordnungen. Studio und fachuebergreifende Belegzuordnung
  gehoeren zur Plattform; keine neue Domäne oder Containergrenze.
- MCP-Referenz aus korrigiertem Registry-Vertrag regeneriert.

## Grenzen

Dies ist der authentifizierte HTTP-Ausfuehrungsadapter im ERP-Backend.
Der separate AI-Dienst wird damit nicht automatisch zum verbundenen Client;
dessen Platzhalter bleiben nicht verfuegbar. Ein vollstaendiger MCP-Transport
mit Initialisierung/Tool-Discovery und weitere Masken-Schreibadapter bleiben
offen. Kein Endpoint wird allein aufgrund eines Katalogeintrags freigeschaltet.
Approval-pflichtige Tools bleiben bis zur Bindung an eine echte serverseitige
Freigabe nicht ausfuehrbar. Kein vom Aufrufer gesendetes Freigabe-Boolean genuegt.

Der HTTP-Test ersetzt die OIDC-Dependency durch eine Testidentitaet; ein echter
Identity-Provider-Login ist damit nicht abgenommen. UIX/KIM/FSX-Gesamtabnahme
bleibt offen. Migration-Downgrade loescht das Replay-Journal absichtlich nicht,
damit ein Code-Rollback keine doppelten Ausfuehrungen ermoeglicht.
