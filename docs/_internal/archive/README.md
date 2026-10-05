# Archiv (historische Doku-Artefakte)

Revisionssichere Ablage historischer Dokumente. Diese Dateien wurden aus dem
`docs/`-Wurzelverzeichnis hierher verschoben, weil sie abgeschlossene Vorgänge
dokumentieren (Completion-Reports, Debugging-/Fix-Notizen, Summaries, alte
Test-/UAT-Protokolle).

- **Nicht** Teil der veröffentlichten Site.
- **Nicht** aktiv gepflegt.
- Git-Historie bleibt durch `git mv` erhalten.

Kategorien und Zielbuckets: siehe `docs/dokumentation/migrationsplan.md`.

## Abhängigkeits-Manifeste tragen die Endung `.archived`

Die hier archivierten Node-/Python-Projekte (`domains-ts-backend/`,
`l3-migration-toolkit/`, `guacamole-l3-migration/`, `mains/crm/`, `swarm/`) sind
laut [ADR-039](../../adr/adr-039-repo-layout.md) bewusst stillgelegt: nie
produktiv verdrahtet, ihre CI-Workflows wurden entfernt, kein Workflow, kein
Compose-File und kein pnpm-Workspace referenziert sie. Sie werden nicht
installiert, nicht gebaut und nicht ausgeliefert.

Ihre `package.json` und `package-lock.json` heißen deshalb `*.archived`. Grund: GitHubs Dependency Graph erkennt Manifeste am Dateinamen und
erzeugte darauf 44 Schwachstellen-Meldungen — auf Code, der nirgends läuft. Eine
Pfad-Ausnahme für Alerts gibt es nicht (`dependabot.yml` steuert ausschließlich
Update-PRs), also war das Umbenennen der einzige Weg, der die Meldungen an der
Ursache beseitigt, statt sie einzeln stumm zu schalten.

Der Inhalt ist unverändert — die Umbenennung ist ein reines `git mv`, kein Byte
ging verloren. Wer eines der Projekte wiederbeleben will, benennt die Dateien
zurück und zieht die Abhängigkeiten dabei auf aktuelle Stände; die Meldungen
kommen sonst zu Recht zurück.

Ausgenommen ist `swarm/requirements.ui-explorer.txt`: die Datei pinnt keine
Versionen, erzeugt entsprechend keine Meldungen und wird von
`swarm/Dockerfile.ui-explorer` per Pfad referenziert — ein Umbenennen bräche die
Referenz ohne Sicherheitsgewinn.

Neue Manifeste im Archiv bitte direkt mit `.archived` ablegen, sofern sie
Versionen pinnen und nicht aus dem Archiv heraus referenziert werden.
