# Architecture Impact Preflight

Diff-basierte Zuordnung von geänderten Pfaden zu Architekturverträgen, Generatorpflichten und `vor_push.REGISTER`-IDs.

**Status P1:** deklarative Map + Matcher-Bibliothek (ohne CLI, ohne `vor_push`-Wire).  
**Slice:** `ARCH-IMPACT-PREFLIGHT-MAP`  
**Bezug:** PR #232 Generator-Drift (R1b, R2b, R3b, R4a, R5) — Feinplan/Vorschlag im Project-Store.

## Artefakte

| Pfad | Rolle |
| --- | --- |
| `config/architecture-impact-map.yaml` | Source of Truth für Impact-Klassen |
| `scripts/architecture_impact_map.py` | Laden, Schema-Validierung, `match_paths` |
| `tests/test_architecture_impact_map.py` | Unit-Tests + JSON-Fixtures ohne DB |
| `docs/architecture/quality-gates/architecture-drift-checks.md` | bestehende Drift-Gates (Querverweis) |

## Map-Schema (Klasse)

Pflichtfelder pro Klasse:

- `id` (kebab-case, stabil)
- `description`
- `globs` (konservativ, keine Inhaltsheuristik in P1)
- `contracts`
- `generators` (Abhilfe ohne `--check`)
- `checks_dbfree` (für späteren CLI-Modus `--check-dbfree`)
- `register_ids` — **exakte** Namen aus `scripts/vor_push.py` `REGISTER` (Spalte 0)
- `hints` (z. B. `pnpm arch:drift`, require_db-Hinweise)
- `requires_db` (bool)
- optional: `pr232_refs`

Ungültige Map (fehlende Pflichtfelder, unbekannte `register_ids`) → `ImpactMapError`.

## Pflichtklassen (P1)

| id | PR-232 | requires_db |
| --- | --- | --- |
| `api-router` | R2b | nein |
| `service-stem` | R4a | nein |
| `migration-schema` | R5 (Schema) | **ja** |
| `table-consumer` | R3b | nein |
| `baseline-improvement` | R1b | nein |
| `frontend-masks` | — | nein |
| `status-process-studio` | R4b (Hinweis) | Hinweis require_db |
| `finance-gobd` | — | Hinweis Tests/CI |
| `c4-container-adr` | — | nein |
| `agent-handbuch-docs` | — | nein |

## Matcher-Regeln

1. Eine Datei → **Union** aller treffenden Klassen.
2. Unbekannte Pfade unter `app/`, `alembic/`, `modules/`, `packages/frontend-web/` → `unmapped_structural=true` (Fail-safe-Vorbereitung für P3; in P1 nur melden).
3. Keine SQL-/Inhaltsheuristik in P1.
4. DB-pflichtige Gates werden nur gemeldet, nie still als grün behandelt.

## API (Bibliothek)

```python
from architecture_impact_map import load_map, match_paths

impact_map = load_map()  # config/architecture-impact-map.yaml
report = match_paths(["app/api/v1/endpoints/foo.py"], impact_map)
# report.class_ids, report.generators, report.register_ids,
# report.requires_db, report.unmapped_structural
```

Smoke: `python scripts/architecture_impact_map.py` (lädt und validiert die Map).

## Fail-safe (P3-Vorbereitung)

Wenn später `vor_push` selektiv Register filtert:

- `unmapped_structural` oder Map-Fehler → **alle** Register (heutiges Verhalten).
- Selective Register nur hinter explizitem Opt-in; Default off.

## Drift-Checks

Bestehende Generator-/Drift-Gates bleiben Owner:

- `docs/architecture/quality-gates/architecture-drift-checks.md`
- `bash scripts/check_all_doc_generators.sh --check`
- `pnpm arch:validate` / `pnpm arch:drift`

Neue CI-Rotursache der Klasse Generator-Drift → Eintrag in `config/architecture-impact-map.yaml` (analog Regel „neue Ursache → `vor_push.REGISTER`“).

## Nicht in P1

- Kein CLI (`architecture_impact_preflight.py` → P2)
- Kein Import/Aufruf in `vor_push` (→ P3)
- Kein Ausführen echter Generatoren in den Map-Tests
- Keine Änderung bestehender Generatoren

## Folge-Slices

- **P2** `ARCH-IMPACT-PREFLIGHT-CLI` — `--print` / `--json` / `--check-dbfree`
- **P3** `ARCH-IMPACT-PREFLIGHT-WIRE` — `vor_push`-Anbindung + AGENTS-Anti-Loop
