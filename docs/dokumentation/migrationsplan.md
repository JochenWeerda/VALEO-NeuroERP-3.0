---
title: Doku-Migrationsplan
type: explanation
audience: [entwickler, product, docs]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.3.0
---

# Doku-Migrationsplan

Vorgehen zur Überführung der organisch gewachsenen Altbestände in die kuratierte
Diátaxis-Struktur — schrittweise, nachvollziehbar, ohne Informationsverlust.

## Leitlinien

- **Nichts löschen.** Historisches wird nach `docs/_internal/archive/`
  verschoben (`git mv`, Historie bleibt erhalten).
- **Kuratiert vor vollständig.** Aktiv gepflegte Inhalte wandern in die
  Fachbereiche; Reste bleiben archiviert, bis sie kuratiert werden.
- **Build bleibt grün.** Altbestände sind per `exclude_docs` vom Build
  ausgenommen; Architektur nur kuratierte Whitelist; alle ADRs sind seit
  Phase G in der Site (Wave-STATUS bleibt repo-only).

## Kategorien → Zielbucket

| Kategorie (Beispiele) | Zielbucket |
|---|---|
| Completion-Reports (`PHASE-*-COMPLETION-REPORT`, `*-COMPLETE`, `*-complete`) | `docs/_internal/archive/` |
| Debugging-/Fix-Notizen (`*-debugging`, `*-fix`, `*-fixed`, `*-root-cause`) | `docs/_internal/archive/` |
| Summaries (`*-summary`, `*-zusammenfassung`) | `docs/_internal/archive/` |
| Alte Test-/UAT-Protokolle (`*-test-*`, `*-uat-*-protokoll`) | `docs/_internal/archive/` |
| Benutzeranleitungen (aktiv) | `docs/benutzerhandbuch/` |
| Admin/Betrieb (aktiv) | `docs/admin/` |
| Schnittstellen (generiert) | `docs/schnittstellen/` |
| Architektur/ADR | `docs/architecture/`, `docs/adr/` (Nav: Entwickler) |
| Compliance | `docs/compliance/` (Nav: Compliance-Bereich) |
| Workflow-Analyse-Cards (`docs/cards/`) | Intern (`docs/_internal/cards-inventory.md`); Ergebnisse → Workflows/Open-Gaps |

## Phasen

1. **Phase A (dieser Slice):** Internen Bereich etablieren, eindeutig
   historische Root-Artefakte archivieren, Inventar/Plan festschreiben.
2. **Phase B (2026-06-25):** Architektur- und ADR-Bereiche in die Navigation
   aufgenommen (`DOC-MIGRATION-003`); Wave-Ordner weiterhin vom Build ausgeschlossen.
3. **Phase C (2026-06-26, abgeschlossen):** Themen-Cluster CRM, i18n und GAP-Analysen
   liegen in `_internal/archive/` (`crm-legacy`, `i18n-legacy`, `repo-archive`).
   **Cards-Audit:** 148 Cards inventarisiert;
   Ketten-Registry [`workflow-chains.md`](../_internal/workflow-chains.md);
   Frontmatter auf alle Registry-Prozess-Cards migriert
   (`scripts/migrate-cards-frontmatter.py`); P2P-010 Overview angelegt.
   Cards bleiben intern; Ergebnisse fließen in Workflows/Open-Gaps.
   Duplikat-Dateinamen (140 gesamt) sind im Inventar klassifiziert: alle strukturell
   harmlos (Process-Kernel-`STATUS.md`, Cards↔Workflows), 0 offene inhaltliche Fälle
   (`DOC-MIGRATION-008`).
4. **Phase D (2026-06-25):** Staleness-Vorbereitung (Frontmatter Compliance/Admin,
   `DOC-MIGRATION-006`) und blockierendes CI-Gate 365 Tage (`DOC-MIGRATION-007`).
5. **Phase E (2026-06-26):** Bulk-Archivierung ~390 Alt-Dokumente nach
   `docs/_internal/archive/` (`scripts/docs-legacy-migrate.py`); Doppel-Archiv
   `docs/archive/` aufgelöst; Root von 107 auf 2 kuratierte Dateien reduziert
   (`index.md`, `MASKEN.md`). Duplikat-Dateinamen (140) im Inventar dokumentiert;
   inhaltliche Zusammenführung nur über Bucket-README-Indexe, kein Löschen.
6. **Phase F (2026-06-25):** Card-Duplikat `INV-001` (`inventory/` → kanonisch
   `lager/`) aufgelöst; Architektur + ADR in MkDocs-Navigation; Wave-Ordner
   weiterhin per `exclude_docs` vom Build ausgeschlossen (`DOC-MIGRATION-003`).
7. **Phase G (2026-06-25):** Alle ADR-Dateien in MkDocs-Build aufgenommen;
   Code-Fence-Fix in `adr-014-service-layer-pattern.md` (Pygments/`anchor_linenums`).
8. **Phase H (2026-06-25):** Compliance-Unterseiten in Navigation; Admin
   BRANDING/NUMBERING eingebunden (`DOC-MIGRATION-004`).
9. **Phase I (2026-06-25):** Abgearbeitete Roadmap-Snapshots und Legacy-
   Planungsdocs gelöscht (~23 Dateien); Verweise auf Process-Kernel/Open-Gaps;
   `python scripts/docs-legacy-migrate.py --purge-roadmap --apply`
   (`DOC-MIGRATION-005`).
10. **Phase J (2026-06-25):** Frontmatter auf Compliance-/Admin-Seiten;
    `docs/operations/` archiviert (`DOC-MIGRATION-006`).
11. **Phase K (2026-06-26):** Migrationsprogramm abgeschlossen — Inventar 0
    Archiv-Kandidaten; Duplikat-Klassifikation; `docs/index.md` aktualisiert;
    Verweis in Open-Gaps (`DOC-MIGRATION-008`).

## Abschluss (2026-06-26)

Das Bulk-Migrationsprogramm **DOC-MIGRATION-001…008** ist abgeschlossen:

| Ergebnis | Stand |
|----------|-------|
| Root-`.md` | 2 kuratierte Dateien (`index.md`, `MASKEN.md`) |
| Archiv | ~430 Dateien unter `docs/_internal/archive/` |
| MkDocs-Nav | Diátaxis-Bereiche, Compliance, Architektur, alle ADRs |
| CI-Gates | Staleness blockierend (365 Tage, 47 kuratierte Seiten) |
| Roadmaps | Abgearbeitete Snapshots gelöscht; Redirect über `docs/roadmap/README.md` |
| Lieferstand | [Process Kernel STATUS](../architecture/process-kernel/STATUS.md), [Open Gaps](../project-context/open-gaps-and-known-issues.md) |

**Fortlaufende Pflege:** Neue Doku direkt in Diátaxis-Bereichen anlegen; Altbestände
nur über `scripts/docs-legacy-migrate.py` archivieren; Cards intern halten.

## Sicherheitsnetz

- Vor jeder Verschiebung Working-Tree-Status prüfen (keine fremden, offenen
  Änderungen an Zieldateien).
- Verschiebungen bevorzugt per `git mv`; **Ausnahme:** eindeutig abgearbeitete
  Roadmap-Snapshots dürfen per `--purge-roadmap` entfernt werden.
- Bei Unsicherheit: Datei im Archiv belassen statt voreilig kuratieren.
