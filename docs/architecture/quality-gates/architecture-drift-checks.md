# Architecture Drift Checks

Katalog der Gates für Architecture OS (bestehend + neu).

## Generatoren (`pnpm arch:validate`)

| Check | Skript |
|---|---|
| C4 Views | `scripts/render_c4_views.py --check` |
| Architecture Index | `scripts/generate_architecture_index.py --check` |
| Container Inventar | `scripts/generate_container_inventory.py --check` |
| OpenAPI | `scripts/generate_openapi.py --check` |
| Code-Inventare | `scripts/generate_code_inventories.py --check` |
| Agent-Handbuch | `scripts/generate_agent_handbuch.py --check` |

Aufruf gebündelt: `scripts/check_all_doc_generators.sh --check`

## Domänen-Drift (`pnpm arch:drift`)

| Check | Regel |
|---|---|
| Prefix-Regeln | `config/architecture-domain-prefixes.yaml` — Single Source of Truth |
| Unmapped routes/services/endpoints | **0 erlaubt** in strict (`--require-complete`) |
| Route-Fallback | Erst `path`-Segment, dann `@/pages/<folder>/` aus `module` |
| DSL containers | Kernelemente in `workspace.dsl` vorhanden |

Strict-Modus: `python scripts/architecture_drift_check.py --strict` — erzwingt vollständiges Mapping + Generator-Drift.

Prefix-Regel ergänzen: Eintrag in `architecture-domain-prefixes.yaml` → `python scripts/generate_architecture_index.py` → `--require-complete` prüfen.

## Unit-Tests

`pnpm test:arch-index` — 7 Tests für Prefix-Matching und Vollständigkeit (`--no-cov`, da isolierter Lauf sonst am globalen `fail-under=60` scheitert).

## CI

- [quality-gate.yml](../../../.github/workflows/quality-gate.yml) — `pnpm arch:validate`
- [docs.yml](../../../.github/workflows/docs.yml) — Doc-Generatoren

## Bei Failure

1. Generator lokal ohne `--check` ausführen
2. Diff committen
3. Impact Note aktualisieren
