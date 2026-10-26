---
title: Abgleich vor migrate:apply (2026-10-26)
type: qa
audience: [entwickler, qa, betrieb]
owner: Claude Code
status: active
last_reviewed: 2026-10-26
---

# Abgleich vor migrate:apply (2026-10-26)

Slice `DRIZZLE-APPLY-GUARD-20261026`, Zweig `claude/drizzle-apply-guard-20261026`, gestapelt
auf PR #45 ([drizzle-chains-8-20261026.md](drizzle-chains-8-20261026.md)).

## Befund (lesend geprueft)

- **Kein Push-Altbestand.** Kein Compose-File, keine Pipeline und kein Deployment startet die
  TS-Domaenendienste; auf dem lokalen Server gibt es keine Domaenendatenbanken
  (`*_db`, `crm`, `scheduler` …), nur `valeo_neuro_erp`, Pruefstaende und Fremddienste.
  Keine der 61 Drizzle-Tabellen liegt in Drizzle-Form vor; namensgleich existieren nur
  Backend-Tabellen anderer Struktur (`public.documents`, `public.opportunities`,
  `domain_*`-Schemata).
- **Absicht:** `.env.example`/README sehen je Dienst eine eigene Datenbank vor.
- **Risiko:** analytics, audit, contracts, document, notifications, pricing, quality,
  regulatory und weighing loesen die URL zuerst aus `DATABASE_URL` auf, der Variable der
  Backend-Hauptdatenbank (im Root-Arbeitsbaum gesetzt). `migrate:apply` haette dort
  Domaenentabellen in `public` und ein Schema `drizzle` angelegt; document waere an
  `public.documents` halb gescheitert.
- `packages/quality-domain/scripts/setup.sh` rief `migrate:up` (Snapshot-Upgrade) in der
  Absicht, Migrationen anzuwenden, und verschluckte Fehler.

## Aenderung

`scripts/drizzle_apply_guard.cjs` vor `drizzle-kit migrate`:

- loest `drizzle.config.ts` ueber das paketeigene `tsx` auf (gleiche Env-Reihenfolge wie
  drizzle-kit; Ausgabe per Markierung von dotenv-Bannern getrennt; keine Zugangsdaten in der Ausgabe);
- prueft das Zielschema (`current_schema()`): `alembic_version` oder kettenfremde Tabellen ->
  Abbruch `foreign-target`; Kettentabellen ohne Journal -> Abbruch `unjournaled-tables`
  (Abgleich mit Snapshot noetig); Journal vorhanden -> `incremental`; leer -> `fresh`;
- startet erst dann das paketeigene drizzle-kit (ueber `node`, ohne Shell).

`migrate:apply` laeuft in allen elf Paketen ueber den Waechter, `migrate:check` nur die
Vorpruefung. quality `setup.sh` ruft `migrate:apply` und zeigt dessen Fehler. Runbook Phase 2
nennt `migrate:check`.

## Abnahme

| Pruefung | Ergebnis |
| --- | --- |
| `node --test scripts/verify_drizzle_apply_guard.cjs` | 5/5 (fresh, incremental, alembic, Fremdtabelle trotz Journal, Kettentabellen ohne Journal) |
| `migrate:check` aller elf Pakete gegen `valeo_neuro_erp` (lesend) | 11x `foreign-target`, Exit 2; kein Schema `drizzle` entstanden |
| `migrate:check` audit gegen `valeo_probe` (lesend) | `foreign-target`, Exit 2 |
| `pnpm --filter … run migrate:check` | Waechter greift auch ueber pnpm (Exit 2) |
| valeo_probe, eigenes Schema `drizzle_guard_check` (Nutzerfreigabe) | 1. leer: `fresh`, angewendet, 2 Tabellen, Journal 1; 2. erneut: `incremental`, Journal 1; 3. Journal entfernt: `unjournaled-tables`, Exit 2, nichts geaendert |

Pruefstand: vorher/nachher `pruefstand_db.py --status` Revision `loading_stop_fk_20261023`,
keine fremde Sitzung; Restkontrolle 0 (`drizzle`, `drizzle_guard_check` und fruehere
Pruefschemata). Ein erster Lauf scheiterte, bevor etwas angewendet wurde (drizzle-kit
exportiert `bin.cjs` nicht); behoben, Lauf im selben Fenster wiederholt.

## Grenzen

- Der Waechter schuetzt `migrate:apply`/`migrate:check`. Ein direkter Aufruf von
  `drizzle-kit migrate` oder `push` umgeht ihn. Die Laufzeitverbindungen der Dienste
  fallen weiterhin auf `DATABASE_URL` zurueck (nicht Teil dieses Slices).
- Fuer `unjournaled-tables` gibt es bewusst keinen automatischen Abgleich, weil kein
  solcher Bestand existiert; der Fall stoppt mit Tabellenliste.
- Keine Aussage ueber vollstaendige Sicherheit oder Gesamtfreigabe.

## CI-Abnahme

| Lauf | Commit | Ergebnis |
| --- | --- | --- |
| Security Scan 40284224057 | d3fa29fb8 | alle Jobs success |
| Quality Gate 40284221002 | d3fa29fb8 | Dependency Scan, Improvement integrity, FSX, Secret Scan, SBOM, WCAG, Production contract u. a. success; Frontend-Unit 214 Faelle mit identischer Fallmenge wie Basis-Lauf 40234161888 (0 neu); Doc-Drift 272 wie Basis |
