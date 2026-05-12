# VALEO NeuroERP - Agent Operating Guide

## Zweck

Diese Datei ist der schnellste Einstieg fuer jeden Agenten, der in diesem Repository arbeitet.

Sie ersetzt nicht die fachliche Dokumentation, sondern legt die verbindliche Startreihenfolge und die Zusammenarbeit mit parallelen Agenten fest.

## Pflichtreihenfolge bei Session-Start

1. [docs/README.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/README.md)
2. [Process Kernel Status](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/architecture/process-kernel/STATUS.md)
3. [Agent Ops README](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/README.md)
4. [Active Workboard](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/active-workboard.md)
5. relevante Dateien unter `docs/project-context/`
6. relevante Dateien unter `docs/workflows/` und `docs/quality-assurance/`

## Nicht verhandelbare Regeln

- Source of Truth fuer Lieferstand ist `docs/architecture/process-kernel/STATUS.md` plus relevante `wave-*/STATUS.md`.
- Vor jeder Umsetzung zuerst Doku und bestehende Entscheidungen lesen.
- Keine stillen Annahmen: Annahmen explizit machen und dokumentieren.
- Keine blinden Reverts fremder Aenderungen.
- Bei paralleler Arbeit immer einen klaren Dateibesitz oder Themenbesitz definieren.
- Nach jeder relevanten Aenderung Tests, Doku und Workboard aktualisieren.

## Parallelbetrieb mit zwei oder mehr Agenten

- Ein Agent ist `Lead` fuer Priorisierung und Integration.
- Jeder Agent arbeitet auf einem klar abgegrenzten Slice.
- Jeder Slice bekommt:
  - Ziel
  - Dateibesitz
  - Abnahmekriterien
  - offene Risiken
- Gemeinsamer Koordinationspunkt ist:
  - [Active Workboard](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/active-workboard.md)

### Claim-Pflicht (verbindlich)

Bevor ein Agent mit einem Slice beginnt:

1. Workboard lesen — Slice muss `offen` sein.
2. Slice auf `reserviert` setzen + Owner eintragen.
3. **Sofort committen:** `chore(workboard): claim SLICE-ID`
4. Erst danach mit der Arbeit beginnen.

Kein Agent darf einen Slice mit Status `reserviert` oder `in arbeit` uebernehmen.

Vollstaendiges Protokoll: [Parallel Work Protocol](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/parallel-work-protocol.md)

## Restart-Regel

Wenn eine Session neu startet:

- zuerst `AGENTS.md`
- dann `docs/agent-ops/session-start-checklist.md`
- dann `docs/agent-ops/active-workboard.md`
- dann den letzten passenden Handoff / Resume-Block lesen

## Nuetzliche Repo-Befehle (ERP-Domain / Finanz)

- **`pnpm test:erp-domain`** — Jest nur fuer `packages/erp-domain` (`*.spec.ts`).
- **`pnpm migrate:erp-finanz`** — SQL `001_finance_core` + `003_finanz_tenant_id` (Verbindung: `ERP_DATABASE_URL` → `DATABASE_URL` → `CRM_DATABASE_URL`; `.env`-Laden siehe `tools/migration/run_sql_migration.ts`). Fachlich: [docs/erp-finanz-multitenancy.md](docs/erp-finanz-multitenancy.md).

## Verweise

- [Agent Ops README](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/README.md)
- [Parallel Work Protocol](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/parallel-work-protocol.md)
- [Handoff Template](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/handoff-template.md)
- [Resume Packet Template](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/agent-ops/resume-packet-template.md)
