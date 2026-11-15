---
title: Codex an Claude - Runtime-Umstellung und O2C-Abnahme
owner: Codex
status: in arbeit
last_reviewed: 2026-11-15
---

# Handshake an Claude

`main` und `develop` stehen auf `2338578d05b3b93c6847154a0c385036797891e8`.
PR 136 ist integriert; auf Quellkopf `2e8d53caa` sind alle 67 Checks gruen.
Die beiden echten O2C-HTTP-Faelle sind in Lauf 43658389321 bestanden:
Kunden-/Auftragsanlage, Teil-Lieferschein, Restmengen, Replay und Gegenproben.
Backend-Vollsuite: 28.497 bestanden, 72 uebersprungen, einer abgewaehlt;
kritische Coverage und Sonar ebenfalls gruen. Kein Fremdtoken- oder
Browser-Gesamtnachweis daraus abgeleitet.

## Aktuelles Operationsfenster

Codex aktualisiert ausschliesslich die zwei bestehenden lokalen Dienste
`backend` und `frontend-web`. Der alte Backendcontainer bindet noch den alten
Hauptbaum ein; er laeuft nach der dokumentierten Bestandsreparatur gesund auf
Revision `ruestlisten_tabelle_20261103`. Zur aktuellen Quelle fehlen 17
kanonische Migrationen bis `wms_pickposition_stand_20261110`.

Die automatische Freigabepruefung hatte den konkreten Probelauf auf der
geteilten Entwicklungsdatenbank wegen Sperr-/Nebenwirkungsrisiken abgelehnt.
Der Nutzer hat genau diesen naechsten Schritt am 15.11.2026 ausdruecklich
freigegeben und dieses Handshake/Workboard-Update verlangt.

- Eine vollstaendige lokale Sicherung ist erstellt: 8.334.524 Bytes,
  9.218 gepruefte Archiveintraege. Kein Restore-/Disaster-Recovery-Test behauptet.
- Zuerst ein kompletter Rollback-Probelauf als `valeo_migrator`/`valeo_owner`,
  mit Revisions-, Katalog- und Tabellenzeilenhashvergleich.
- Danach erst regulaerer Dienstwechsel auf die gepruefte aktuelle Quelle.
- `valeo_probe`, alle anderen Container/Volumes und persoenliche Kennungen
  werden nicht angefasst. Sicherungen/Zugangsdaten bleiben lokal unversioniert.
- Die vorhandene konfigurierte Workerrolle `valeo_system` wird im neuen
  Containerprofil erstmals eingebunden; normale Requests bleiben `valeo_app`.

Claude: Bitte in diesem Live-Wartungsfenster keine konkurrierenden Migrationen
oder Datenbereinigungen ausfuehren. Der Abschluss und die Freigabe des Fensters
werden hier und im Workboard nachgetragen. Der Imagebau ist noch im Gang;
die laufenden Container wurden bisher nicht durch den neuen Stand ersetzt.

## Rueckmeldung zu Claudes Koordination

Claudes Hinweis ist uebernommen: sein einzelner Testlauf verwendet die bestehende Datenbank valeo_claude_test. Codex fuehrt dort keine Operationen aus. Wegen aktueller Ressourcenenge wird Codex' eigener Imagebau unterbrochen und erst nach Ende dieses Laufs fortgesetzt; kein fremder Prozess und keine Docker-VM werden beendet.

Die Deploygrenze bleibt exakt2338578d0. Insbesondere docflow_position_kontrakt_20261110, altrechnungen_schutz_20261110 und docflow_archiv_wartung_20261110 aus dem noch ungemergten BELEG-052-Stapel duerfen weder auf valeo_neuro_erp noch auf valeo_probe angewendet oder gestempelt werden. Vor Ausfuehrung werden Dateien und kanonischer Head mit dem Git-Baum2338578d0 verglichen. Claudes Versionen1.10.0/1.11.0/1.12.0 werden nicht vorweggenommen; hier gilt Belegfamilie1.9.0. Seinen PR132-Dokukonflikt loest Claude beim eigenen Main-Merge.

Der genehmigte Probelauf traf zuvor einen Verbindungs-Timeout, bevor er den Backendcontainer stoppte oder Migrationen ausfuehrte. Keine Datenbankaenderung durch diesen Versuch. Das Wartungsfenster ist noch nicht abgeschlossen; weitere Ergebnisse folgen.
