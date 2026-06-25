# Interner Doku-Bereich (nicht veröffentlicht)

Dieser Bereich (`docs/_internal/`) ist **kein** Teil der veröffentlichten
MkDocs-Site. Er ist in `mkdocs.yml` per `exclude_docs` ausgeschlossen und von den
Doku-Hygiene-Checks (`docs-markdown-check`, `docs-governance-check`) ausgenommen.

## Zweck

- **archive/** — revisionssicher aufbewahrte, historische Artefakte
  (Completion-Reports, Debugging-Notizen, Summaries, alte Testprotokolle).
  Nichts wird gelöscht; die Git-Historie bleibt erhalten.

## Regeln

- Inhalte hier sind **historisch** und werden nicht aktiv gepflegt.
- Aktive, kuratierte Doku gehört in die Fachbereiche unter `docs/` (siehe
  `docs/dokumentation/dokumentationskonzept.md`).
- Wird ein archiviertes Dokument wieder relevant, wird sein Inhalt in eine
  kuratierte Seite überführt (nicht das Archiv-Dokument in die Nav aufnehmen).

Siehe `docs/dokumentation/migrationsplan.md` für das Vorgehen.
