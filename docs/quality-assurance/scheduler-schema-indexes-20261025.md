---
title: scheduler-Schema unter drizzle-orm 0.45 ladbar (2026-10-25)
type: qa
audience: [entwickler, qa]
owner: Claude Code
status: active
last_reviewed: 2026-10-25
---

# scheduler-Schema unter drizzle-orm 0.45 ladbar (2026-10-25)

Slice `SCHEDULER-SCHEMA-INDEXES-20261025`, Zweig `claude/scheduler-schema-indexes-20261025`,
Basis `68fab0da7` (PR #42, [drizzle-kit-031-20261025.md](drizzle-kit-031-20261025.md)).

## Befund

`packages/scheduler-domain/src/infra/db/schema.ts` baute drei Indizes
(`schedule_runs_idx`, `job_runs_idx`, `runs_tenant_time_idx`) als eigene Exporte ausserhalb
der Tabellendefinition. drizzle-orm 0.45 wirft dabei beim Modulimport
`SyntaxError: "undefined" is not valid JSON`. `src/infra/db/connection.ts` importiert das
Schema, der Dienst konnte so nicht starten; drizzle-kit brach beim Laden ab. Die Exporte
hatten keine Verwender. Messung ueber alle 13 drizzle-Schemata der Domaenenpakete
(`tsx`-Import): nur scheduler betroffen.

## Aenderung

Die drei Indizes stehen jetzt mit unveraenderten Namen und Spalten im Tabellen-Callback von
`runs`; die losen Exporte entfallen. Keine Migrationen vorhanden, also kein Migrationsbedarf.
Regressionstest `tests/unit/db-schema.test.ts` laedt das Schema und prueft die drei Indizes.

## Abnahme (offline, ohne Datenbank, ohne Container)

- Regressionstest gegen das alte Schema rot (`"undefined" is not valid JSON`), mit Fix gruen.
- Paketsuite: 9 failed / 24 passed (Basis 9 failed / 23 passed; die 9 vorbestehend roten
  Faelle in `scheduling-service.test.ts` haben eine andere Ursache: Promise statt Date,
  Validierung wirft statt Ergebnis zu liefern; nicht geaendert).
- `tsc --noEmit`: 11 Fehler, Fehlermenge identisch zur Basis.
- `drizzle-kit generate` ins Scratch-Verzeichnis: 5 Tabellen, `runs` mit 10 Indizes, die drei
  Indizes als `CREATE INDEX ... ("schedule_id","status")`, `("job_id","status")`,
  `("tenant_id","created_at")`; keine Warnung zu doppelten Indexnamen.
- Keine Aussage ueber vollstaendige Sicherheit oder Gesamtfreigabe.
