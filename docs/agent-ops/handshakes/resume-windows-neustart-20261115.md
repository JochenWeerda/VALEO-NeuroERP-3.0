---
title: Wiederaufnahme nach Windows-Neustart am 15.11.2026
owner: Codex
status: wiederaufgenommen und SQL-Fenster abgeschlossen
last_reviewed: 2026-11-15
---

# Resume: LOCAL-RUNTIME-2338578-20261115

Aktualisierung: Wiederaufnahme abgeschlossen, 17 freigegebene Migrationen regulaer
angewendet, Backend und Frontend gesund. Die folgenden Neustartnotizen beschreiben
den historischen Unterbrechungsstand und sind keine Aufforderung zur Wiederholung.
Aktueller Nachweis: docs/quality-assurance/local-runtime-2338578-20261115.md.

## Arbeitsort und Git-Stand

Ausschliesslich in diesem bereits verwendeten Arbeitsbaum weiterarbeiten:
`C:/Users/Jochen/VALEO-NeuroERP-3.0/artifacts/psm-zulassungen-20261104`.
Der primaere Baum `C:/Users/Jochen/VALEO-NeuroERP-3.0` ist als Laufzeitquelle
veraltet; dort keine Aenderungen blind uebernehmen oder zuruecksetzen.

Aktueller Arbeitszweig: `codex/runtime-deploy-20261115`.
`main` und `develop` wurden auf GitHub auf
`2338578d05b3b93c6847154a0c385036797891e8` synchronisiert.
PR 136 ist integriert, alle 67 Checks auf Quellkopf `2e8d53caa` waren gruen.
Beide echten O2C-HTTP-Faelle sind belegt; Backend 28.497 bestanden,
72 uebersprungen, einer abgewaehlt; kritische Coverage und Sonar gruen.

## Warum jetzt angehalten wurde

Der Nutzer faehrt Windows selbst herunter, weil Docker nicht mehr antwortet.
Es werden bis zur Rueckmeldung nach dem Neustart keine weiteren Builds,
Migrationen, Prozessabbrueche oder Docker-/WSL-Neustarts durch Codex gestartet.
Eigener Build ist abgebrochen, ein dazugehoeriger Buildclient war danach
nicht mehr auffindbar. Docker lieferte zuletzt Fehler 500; PostgreSQL lief
in einen Verbindungs-Timeout. Der aktuelle Gesundheitszustand ist unbestaetigt.

Die Zustimmung zum konkreten Probelauf der 17 kanonischen Migrationen auf
`valeo_neuro_erp` wurde am 15.11.2026 ausdruecklich erteilt. Der Versuch nach
Zustimmung scheiterte bereits beim Verbindungsaufbau: vor Dienststopp,
DDL/DML oder Migration. Kein erfolgreicher Probelauf und kein aktueller
Deploy behauptet. Die Zustimmung bleibt dokumentiert; nach Neustart zuerst
Ziel, Zustand und konkurrierende Nutzung erneut pruefen.

## Sicherungen und lokale Artefakte

Nur lokal, ignoriert und nicht nach GitHub uebertragen:
`artifacts/local-runtime-2338578-20261115/`.

- `before-upgrade.full.dump`: vollstaendige komprimierte Sicherung der
  Entwicklungsdatenbank, 8.334.524 Bytes; `pg_restore --list` bestaetigte
  9.218 Archiveintraege. Das ist kein vollstaendiger Restore-Drill.
- `before-images-and-mounts.json`: vorherige Image-IDs und Mounts der beiden
  Anwendungscontainer; keine Zugangsdaten enthalten.
- `build.log`: Backendbau nach Log weit fortgeschritten; neuer Frontendbau
  beim Rendern der Chunks unterbrochen. Beide Imagezustaende nach Neustart
  ueber die Engine verifizieren; bestehende Container wurden nicht ersetzt.
- `rehearse_pending.py`: vorbereiteter, stets zurueckgerollter Operationslauf.
  Nicht ungeprueft starten: vorher die Quellgrenze und das Ressourcenfenster
  verifizieren. Er umgeht bewusst `alembic/env.py`, das eine eigene Verbindung
  oeffnen und explizit committen wuerde.
- `source-2338578d0.tar.incomplete`: fehlgeschlagener Quellarchivexport,
  ausdruecklich unbrauchbar; weder entpacken noch als Freigabenachweis verwenden.
- `lfs-source-metadata.json`: Quellmetadaten; kein fertig gepruefter Export.

Vertrauliche Konfiguration liegt weiterhin in der bestehenden Root-`.env`.
Nur im Speicher bzw. als bestehende Dateiquelle verwenden; keine Werte,
Kennwoerter, persoenlichen Kontonamen oder E-Mails ausgeben/versionieren.
Die vorhandenen unversionierten `.husky/_`-Hooks nicht mitsichern/committen.

## Verbindliche Grenze zu Claude

Claude nutzt die bestehende `valeo_claude_test`; Codex fasst sie nicht an.
Sein Testprozess wurde nicht beendet. Vor dem eigenen ressourcenintensiven
Build seinen Testabschluss bzw. das gemeinsam freie Fenster bestaetigen.
Keine neuen Datenbanken oder Container pro Test/Agent anlegen; `valeo_probe`
nur nach Status-/Nutzungspruefung verwenden und niemals implizit zuruecksetzen.

Nur Migrationen aus `2338578d0` duerfen in diese Umstellung eingehen.
487 Migrationsdateien wurden zuvor gegen diesen Git-Baum verifiziert;
kanonischer Head: `wms_pickposition_stand_20261110`.
Insbesondere KEIN Anwenden/Stempeln von:

- `docflow_position_kontrakt_20261110`
- `altrechnungen_schutz_20261110`
- `docflow_archiv_wartung_20261110`

Diese BELEG-052-Kette ist noch nicht in main. Fuer dieses Fenster gilt
Belegfamilie 1.9.0; 1.10.0/1.11.0/1.12.0 nicht vorwegnehmen.
Claudes PR 132 kann beim Workboard einen kleinen Konflikt bekommen; Claude
hat die eigene Aufloesung beim Main-Merge angekuendigt. Nichts blind revidieren.

## Naechste konkrete Schritte nach dem Neustart

1. AGENTS, Session-Start-Checkliste, diesen Resume-Block, Workboard und
   `codex-an-claude-runtime-20261115.md` lesen. Gitstatus/Branch kontrollieren.
2. Mit kurzen Zeitlimits Docker-API, laufende Container, Host-/VM-Speicher,
   Datenbankidentitaet, Revision und fremde aktive Sitzungen nur lesend pruefen.
   Zuletzt bestaetigte Live-Revision: `ruestlisten_tabelle_20261103`.
3. Mit Claude ein freies schweres Ressourcenfenster einhalten. Keine
   parallelen grossen Tests und Imagebuilds. Images nacheinander bauen;
   bei Bedarf nur den eigenen Backenddienst im genehmigten Fenster pausieren,
   keine fremden Dienste, Datenbanken, Volumes oder die VM zwangsweise beenden.
4. Quell-/Migrationsdateien erneut gegen exakt `2338578d0` pruefen, auch auf
   neue unversionierte Migrationen. Kein Upgrade auf einen Claude-Branch.
5. Sicherung pruefen, genehmigten Rollback-Probelauf mit Rollen-, Revisions-,
   Katalog- und Zeilenhashvergleich ausfuehren. Bei Fehler atomar abbrechen,
   den alten Backenddienst wieder starten und den konkreten Befund klaeren.
6. Erst nach Erfolg die beiden bestehenden Dienste `backend` und
   `frontend-web` im Projekt `valeo-neuro-erp` aktualisieren, ohne weitere
   Dienste/Volumes neu anzulegen. Freigegebene Quelle dauerhaft fixieren;
   die neuen Images nicht mit alten oder spaeter veraenderten Bindmounts
   ueberschreiben. Keine unvollstaendige Quellkopie verwenden.
7. Regulären Head, nicht privilegiertes `valeo_app`, begrenzte Workeranbindung,
   Container-Health, /health, unauthentifiziertes DocFlow und Browser-Login-Grenze
   testen. Neue positive Browser-/Fremdtoken-Fachabnahme erst nach echtem Lauf
   behaupten. Workboard, Handshake und QA fortschreiben, committen und pushen.

Das Gesamtziel ist weiterhin offen; Vorbereitung zum Neustart ist kein
Abschluss der lokalen Bereitstellung oder aller Studio-/Matrix-Restpunkte.

