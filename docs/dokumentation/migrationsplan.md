---
title: Doku-Migrationsplan
type: explanation
audience: [entwickler, product, docs]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.2.0
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
| Architektur/ADR | `docs/architecture/`, `docs/adr/` (Nav-Einbindung folgt) |
| Compliance | `docs/compliance/` |
| Workflow-Analyse-Cards (`docs/cards/`) | Intern (`docs/_internal/cards-inventory.md`); Ergebnisse → Workflows/Open-Gaps |

## Phasen

1. **Phase A (dieser Slice):** Internen Bereich etablieren, eindeutig
   historische Root-Artefakte archivieren, Inventar/Plan festschreiben.
2. **Phase B (2026-06-25):** Architektur- und ADR-Bereiche in die Navigation
   aufgenommen (`DOC-MIGRATION-003`); Wave-Ordner weiterhin vom Build ausgeschlossen.
3. **Phase C:** Verbleibende Themen-Cluster (CRM, i18n, GAP) konsolidieren und
   einordnen. **Cards-Audit (2026-06-26):** 148 Cards inventarisiert;
   Ketten-Registry [`workflow-chains.md`](../_internal/workflow-chains.md);
   Frontmatter auf alle Registry-Prozess-Cards migriert
   (`scripts/migrate-cards-frontmatter.py`); P2P-010 Overview angelegt.
   Cards bleiben intern; Ergebnisse fließen in Workflows/Open-Gaps.
4. **Phase D:** Staleness-Gate verschärfen (blockierend), sobald die kuratierte
   Basis vollständig Frontmatter trägt.
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

## Sicherheitsnetz

- Vor jeder Verschiebung Working-Tree-Status prüfen (keine fremden, offenen
  Änderungen an Zieldateien).
- Verschiebungen ausschließlich per `git mv`.
- Bei Unsicherheit: Datei im Archiv belassen statt voreilig kuratieren.
