# Wave 2 - Data, Event and Governance Build-out

**Status:** abgeschlossen
**Datum:** 2026-03-11

## Scope

Wave 2 baut die Event-, Read-Model- und Governance-Plattform fuer Tenants, Rollen, Delegation und Datenresidenz aus.

## Zielbild

Outbox-Events, stabile Read-Models und tenantfaehige Governance-Regeln sollen als produktive Basis fuer Cockpits, Sicherheit und Agentenfaehigkeit dienen.

## Lieferumfang

| AP | Thema | Status |
|----|-------|--------|
| AP1 | Outbox- und Event-Namenskonvention | abgeschlossen |
| AP2 | Read-Models fuer Cockpits, KPIs und Prozessbeobachtung | abgeschlossen |
| AP3 | Tenant- und Verbundmodell | abgeschlossen |
| AP4 | Rollen- und Berechtigungsvererbung | abgeschlossen |
| AP5 | Agenten- und Delegationssicherheitsmodell | abgeschlossen |
| AP6 | Export- und Datenresidenzregeln | abgeschlossen |

## Abnahmekriterien

- Produktive Event-Pfade folgen einer einheitlichen Namenskonvention.
- Read-Models sind als stabile Query-Contracts verfuegbar.
- Tenant-Struktur, Rollenvererbung und Delegationsregeln sind modelliert.
- Datenresidenz- und Exportregeln liefern GoBD-konforme Standardvorgaben.

## Tests

- `pytest tests/test_process_kernel_wave2_events.py tests/test_process_kernel_wave2_read_models.py tests/test_process_kernel_wave2_governance.py -q`
- Compile-Check ueber die betroffenen Kernmodule

## Status

`abgeschlossen`
Stand: 2026-03-11
