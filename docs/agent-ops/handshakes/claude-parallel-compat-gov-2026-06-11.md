# Handshake: Claude Code parallel zu COMPAT-GOV-001

Stand: 2026-06-11
Von: Cursor/Codex-Analyse (User-Jochen)
An: Claude Code (fachliche Vertiefung / Domain-Slices)

## Kontext in einem Satz

Die Grundarchitektur (Multi-Tenant-Monolith, Domain-Schemas, Module-Registry, Mask-Builder, Process-Kernel) bleibt gültig; ergänzt wurde eine verbindliche Kompatibilitäts- und Betriebsschicht — Claude arbeitet an fachlicher Tiefe, Cursor/Codex an Governance/Toolchain/Schema-Hygiene.

## Architekturentscheidung (verbindlich, nicht neu diskutieren)

- **Modul-SemVer allein reicht nicht.** Jedes Release prüft gemeinsam: App/Module, HTTP-API, DB-Schema/Migrationen, Events, Laufzeit/Dependencies.
- **Quelle:** `docs/operations/dependency-and-compatibility-maintenance.md`, `docs/operations/production-readiness-runbook.md`
- **PROD-READINESS-001** ist repo-seitig weitgehend umgesetzt; externe Live-Gates (Cluster, UAT, TSE, Steuer) bleiben blockierend.
- **DB-Änderungen:** Expand/Migrate/Contract — keine destruktiven Schritte ohne Nachweis und Rollback/Forward-Fix.
- **Fachliche Literale** (Enums, Kategorien, Statuswerte) nicht zwischen Modulen kopieren; kanonische Quelle + Validierung an allen Schreibpfaden.
- **Release-Gates** sind fail-closed: fehlende oder hängende Audits/Tests gelten nicht als bestanden.

## Rollenabgrenzung

| Agent | Fokus | Slice-ID |
|-------|-------|----------|
| **Claude Code** | Fachliche Vertiefung (DOM-*-Slices, CRM/KIM, POS-Fachlogik, Domain-Services, UI-Masken) | bestehende DOM-/KIM-/CRM-Slices |
| **Cursor/Codex** | Kompatibilität, Toolchain, Workboard-Hygiene | `COMPAT-GOV-001` ✅, `INV-STOCK-MOVEMENTS-001` ✅ |

**Lead für Priorisierung/Integration:** User (Jochen). Bei Dateikonflikt: Workboard + Integrationsreihenfolge, nicht „wer zuerst committet“.

## Claude: Was du weiter tun sollst

- Domain-Parity, Service-Layer, Mask-Builder-Screens, API-Verträge für **neue** Fachfunktionen.
- Neue Features mit Tests, Toast/Error-Handling, Mutation-Guards (siehe `CLAUDE.md` Invarianten).
- Vor Arbeitsbeginn: Slice im Workboard **claimen** (`chore(workboard): claim SLICE-ID`).
- Nach Abschluss: Handoff-Block im Workboard, Tests grün dokumentieren.

## Claude: Abgeschlossene Governance-Slices (Stand 2026-06-11)

`COMPAT-GOV-001` und `INV-STOCK-MOVEMENTS-001` sind **abgeschlossen**. Die No-Touch-Liste
gilt nicht mehr für neue Arbeit — bei erneuten Governance-Änderungen neuen Slice claimen.

## Claude: Referenz — frühere COMPAT-GOV-001 Dateibesitz (historisch)

Während des Slices galten **keine Änderungen** an:

- `.github/workflows/quality-gate.yml`, `release-gates.yml`, `security-scan.yml`, `ci.yml`
- `requirements.txt`, `scripts/python_deps_install.py`
- `services/finance/**/requirements.txt` (pytest-cov-Pins)
- `tests/conftest.py` (recursionlimit/Coverage-Workaround)
- `scripts/check_required_domain_schemas.py`, `scripts/check_alembic_single_head.py`
- `docs/operations/dependency-and-compatibility-maintenance.md`
- `docs/operations/production-readiness-runbook.md`
- `docs/agent-ops/active-workboard.md` — **nur** eigene Slice-Zeilen; PROD-READINESS-001-Status überlässt du Cursor
- `alembic/versions/*merge*`, `normalize_finance_hr_contracts_20260610.py` (abgeschlossene Readiness-Migrationen)

## Lagerbewegungen (seit INV-STOCK-MOVEMENTS-001)

- **Kanonische Tabelle:** `domain_inventory.inventory_stock_movements`
- **Erledigt:** `articles.py` und `pos_retoure.py` nutzen die kanonische Tabelle; Vertragstests in `tests/test_inventory_stock_movements_canonical.py`
- **Regel für Claude:** Keine neuen Pfade auf `stock_movements`; Lagerbuchungen über kanonische Services/`inventory_stock_movements`
- **Noch offen:** `articles.current_stock`-Update bei POS-Retoure; MHD/Expiry über Chargenstamm

## Pflicht-Lektüre bei Session-Start (Claude)

1. `AGENTS.md`
2. `docs/agent-ops/active-workboard.md` — **zuerst** prüfen, welche Slices reserviert sind
3. `docs/operations/dependency-and-compatibility-maintenance.md` (Kurzüberblick Kompatibilität)
4. `docs/project-context/open-gaps-and-known-issues.md` (offene P1/P2)
5. Relevanter Domain-Slice unter `docs/agent-ops/slices/`

## Verhalten bei parallelen Änderungen

1. `git status` / Workboard lesen — fremde `reserviert`-Slices respektieren.
2. Keine generierten Routing-Artefakte anfassen, wenn fremd-dirty (`route-inventory.gen.json`, `navigation-routes.json`), außer explizit im Slice.
3. Keine Alembic-Migration ohne vorherigen Merge-Head-Check; bei parallelen Migrationen: Merge-Revision im **eigenen** Slice, nicht im Readiness-Slice.
4. Security-/Dependency-Updates (Major): eigener Slice + ADR, nicht „nebenbei“ in Fachfeatures.
5. Wenn du Schema/API brichst: Migrationshinweis + Vertragstest — nicht nur Modulversion bumpen.

## Abnahme vor Commit (Claude, fachliche Slices)

- `tsc --noEmit` / ESLint für betroffenes Frontend
- Fokussierte pytest für betroffene Backend-Pfade
- Keine leeren catch-Blöcke; Mutation-Handler mit pending state
- Workboard-Handoff mit Commit-SHA und Testzahlen

## Eskalation an User

- Brauchst du eine Datei aus COMPAT-GOV-001-Ownership → im Workboard abstimmen, warten oder Integrationsreihenfolge festlegen.
- Unklar ob Tabelle/Enum kanonisch ist → `open-gaps-and-known-issues.md` + `check_required_domain_schemas.py` lesen, nicht raten.
- CI rot nach deinem Commit → zuerst isolierten Test der geänderten Dateien, dann Handoff mit Trace.

## Nächster Schritt Cursor (COMPAT-GOV-001, nicht Claude)

Siehe `docs/agent-ops/slices/COMPAT-GOV-001.yaml`.
