# Interner Doku-Bereich (nicht veröffentlicht)

Dieser Bereich (`docs/_internal/`) ist **kein** Teil der veröffentlichten
MkDocs-Site. Er ist in `mkdocs.yml` per `exclude_docs` ausgeschlossen und von den
Doku-Hygiene-Checks (`docs-markdown-check`, `docs-governance-check`) ausgenommen.

## Zweck

- **archive/** — revisionssicher archivierte Altbestände (~430 Markdown-Dateien,
  konsolidiert aus ehem. `docs/archive/`, Root-Loseblatt-Docs, UAT, Deployment,
  Specs, Wiki, i18n-Legacy u. a.). Bucket-READMEs in Unterordnern.
- **legacy-docs-inventory.md** / **.json** — Inventar + Duplikat-Report
  (`scripts/docs-legacy-migrate.py`).
- **cards-inventory.md** / **.json** — Workflow-Cards (`docs/cards/`).
- **workflow-chains.md** — Ketten-Registry für Cards.
- **archive/cards-duplicates/** — archivierte inhaltliche Card-Duplikate (Stub bleibt am Ursprungspfad).

## Migration (2026-06-26)

Bulk-Archivierung via `python scripts/docs-legacy-migrate.py --apply`:

- `docs/archive/` (178) → `_internal/archive/repo-archive/`
- 105 Root-`.md` → kategorisierte Buckets (`agrar-ernte`, `crm-legacy`, …)
- Legacy-Ordner (`wiki`, `uat`, `deployment`, `specs`, …) → `_internal/archive/<bucket>/`
- **Kuratiert belassen:** `index.md`, `MASKEN.md`, Diataxis-Bereiche, `workflows/`,
  `architecture/`, `agent-ops/`, `project-context/`, `cards/`, `warehouse/` (aktiv)

## Regeln

- Inhalte hier sind **historisch** und werden nicht aktiv gepflegt.
- Aktive, kuratierte Doku gehört in die Fachbereiche unter `docs/` (siehe
  `docs/dokumentation/dokumentationskonzept.md`).
- Wird ein archiviertes Dokument wieder relevant, wird sein Inhalt in eine
  kuratierte Seite überführt (nicht das Archiv-Dokument in die Nav aufnehmen).

Siehe `docs/dokumentation/migrationsplan.md` für das Vorgehen.
