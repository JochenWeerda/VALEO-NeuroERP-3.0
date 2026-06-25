---
title: Doku-Migrationsplan
type: explanation
audience: [entwickler, product, docs]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
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
  ausgenommen; Verschiebungen erzeugen höchstens Warnungen in ebenfalls
  ausgeschlossenen Dateien.

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

## Phasen

1. **Phase A (dieser Slice):** Internen Bereich etablieren, eindeutig
   historische Root-Artefakte archivieren, Inventar/Plan festschreiben.
2. **Phase B:** Architektur- und ADR-Bereiche kuratieren und in die Navigation
   aufnehmen (eigener Slice).
3. **Phase C:** Verbleibende Themen-Cluster (CRM, i18n, GAP) konsolidieren und
   einordnen.
4. **Phase D:** Staleness-Gate verschärfen (blockierend), sobald die kuratierte
   Basis vollständig Frontmatter trägt.

## Sicherheitsnetz

- Vor jeder Verschiebung Working-Tree-Status prüfen (keine fremden, offenen
  Änderungen an Zieldateien).
- Verschiebungen ausschließlich per `git mv`.
- Bei Unsicherheit: Datei im Archiv belassen statt voreilig kuratieren.
