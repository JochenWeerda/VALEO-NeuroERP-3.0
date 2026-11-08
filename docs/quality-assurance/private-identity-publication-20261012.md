# Private Identitaeten vor Veroeffentlichung schuetzen

Stand: 2026-10-12. Claims `IDENTITY-PRIVATE-DATA-20261012` und
`IDENTITY-PRIVATE-PUSH-20261012`.

Persoenliche Administratorzuordnung und Erstkennwort liegen ausschliesslich
ausserhalb des Repositorys. Versionierte Dateien enthalten keine persoenlichen
Kennungen oder Fingerprints. Lokale gesalzene Fingerprints liegen ebenfalls
ausserhalb Git und erlauben die Pruefung ohne Ausgabe der gefundenen Werte.

Die Pfadpruefung blockiert private Identitaetsdateien auch bei erzwungenem
Hinzufuegen. Die Inhaltspruefung kontrolliert vorgemerkte Dateien. Der
`pre-push`-Hook kontrolliert jeden ausgehenden Commit einschliesslich Metadaten
und Merge-Aenderungen; das Entfernen in einem Folgecommit umgeht die Pruefung
nicht. Fehler nennen nur Pfad, Regel und verkuerzte Commitkennung.

Nachweis: sechs datenbankfreie Tests bestanden. Synthetische Git-Historien
pruefen entfernte Inhalte, Merge-Ergaenzungen, Commit-Metadaten, private Pfade
und einen erlaubten Push. Keine echten Kontodaten in den Tests.

## Betriebsregeln fuer alle Agenten

Persoenliche Zugangswerte niemals in Quellcode, Testdaten, Dokumentation,
Workboard, Commitnachrichten oder Remote-URLs schreiben. Die private Ablage
und das Fingerprintmanifest muessen auf jedem Rechner lokal eingerichtet werden.
Ohne Manifest bleibt die Pfadsperre aktiv, eine Pruefung auf bekannte persoenliche
Inhalte ist dort nicht moeglich. CI erhaelt das private Manifest nicht.

Hooks nicht abschalten. Lokale Hooks koennen technisch bewusst umgangen werden;
sie ersetzen keine serverseitige Zugangskontrolle. Vor jedem Push ist ihre
Ausfuehrung zu kontrollieren. Neue private Werte muessen im lokalen Manifest
erganzt werden; der Scanner erkennt keine beliebigen unbekannten Geheimnisse.

Entwicklungsrechte werden als ausdrueckliche, begrenzte Berechtigungen vergeben.
Mandantenbindung, gepruefte Identitaet, Audit und diese Veroeffentlichungssperren
werden dabei nicht umgangen. Authattrappen gehoeren ausschliesslich in isolierte
Testanwendungen. Ein Dienst fuer zeitlich begrenzte Ausnahmeberechtigungen ist
mit diesem Slice noch nicht geliefert.
