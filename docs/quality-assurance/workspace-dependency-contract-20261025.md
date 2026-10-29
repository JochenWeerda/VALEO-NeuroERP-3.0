---
owner: Codex
status: geprueft
last_reviewed: 2026-10-25
---

# Workspace-Abhaengigkeitsvertrag

Die uebernommene Dispositionstafel importiert @dnd-kit/core. Die zuvor nur lokale Installation ist jetzt im Frontendmanifest und im gemeinsamen Lockfile mit 6.3.1 gebunden. Das Lockfile wurde in einer isolierten Manifestansicht erzeugt; die bestehende gemeinsame Installation blieb unveraendert.

Eingefrorene Offline-Installation des Frontends erfolgreich, ohne Installationsskripte und ohne Downloads. Vollstaendige Frontend-Typpruefung ohne Fehler; vier fokussierte Oberflaechensuiten mit 21 Tests bestanden (Entity-Projektion, native Objektrouten, Startseite und Workspace-Zusammensetzung).

Frischer Produktionsaudit: ein bekannter node-forge-Befund, 51 Abhaengigkeitspfade. Strikter Backport-Gate: scanner=1, source_backported=1, blocked=0, release_allowed=true; Laufzeitvertraege bestanden. Nur der Lockhash der bestehenden Pruefnachweise wurde nach unveraenderter Patch- und Manifestpruefung angepasst. Keine neue Ausnahme oder Fristverlaengerung; review_by bleibt 2026-10-28.

Dies ist eine Abhaengigkeitsabnahme. Die Dispositions-Schreibfreigabe bleibt deaktiviert, bis ein serverseitig autoritativer Domain-Command abgenommen ist. Keine Browser- oder Gesamt-CI-Freigabe abgeleitet. Keine Datenbank/Container angelegt.
