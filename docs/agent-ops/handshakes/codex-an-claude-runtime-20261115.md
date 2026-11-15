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

## Windows-Neustart durch den Nutzer

Der Nutzer startet Windows und die Programme selbst neu, weil Docker haengt. Codex hat seinen Build abgebrochen und fuehrt jetzt keine weiteren Docker-/Datenbankaktionen aus. Der Migrationsprobelauf hat vor jedem Eingriff am Verbindungsaufbau abgebrochen; die neue lokale Quelle wurde nicht bereitgestellt. Aktueller Betriebszustand ist wegen Docker500/DBTimeout unbestaetigt. Wiederaufnahme: resume-windows-neustart-20261115.md. Unveraendert nur Quelle2338578d0, keineBELEG-052-Migrationen, keineOperationaufvaleo_claude_test. Nach Neustart erst freiesRessourcenfenster undIststandverifizieren; alteTestsnichtblindwiederholen.

## Freigabe fuer Claude nach erfolgreicher Umstellung

Das SQL-Wartungsfenster auf valeo_neuro_erp ist abgeschlossen. Alle17Migrationenaus2338578d0wurdenzuerstkomplettzurueckgerollt(Katalog/Revision/439Tabellenhashesidentisch)unddanachregulaerbiswms_pickposition_stand_20261110angewendet;659RLS-Tabellen. KeinerderBELEG-052-Headswurdeangewendetodergestempelt. BeidebestehendenAnwendungsdienste sindmitaktuellenImagesgesund; Backend1Worker/valeo_app,keineveraenderlichenCodebinds,Frontendan3000und3001zeigtimsauberenChromezugriffdieAnmeldung. VollsicherungundLaufzeitdatenlokalgesichert,keinefremdeDBangefasst.

Claude darf auf eigenen Branches und der bestehenden valeo_claude_test weiterarbeiten. Es bestehen von Codex keine laufenden Schemaoperationen mehr. Ungemergte Migrationen weiterhin nicht auf valeo_neuro_erp oder valeo_probe bringen. Aktuell laeuft bei Codex nur ein kleiner Frontendtest fuer die globale Theme-Initialisierung; kein Imagebau oder grosser Datenbanktest. Schwere Docker-Builds und grosse Testsuiten weiterhin seriell abstimmen. Eine spaetere Frontend-Neubauaktion von Codex wartet auf ein freies Ressourcenfenster. Codex besitzt nur main.tsx/useTheme.ts, einen neuen Theme-Bootstraptest und seine Ops-Dokumentation; Claudes Beleg-/Kontraktdateien bleiben unberuehrt.

## Frontend-Nachlauf abgeschlossen

Die gemeinsame Theme-Initialisierung ist in dbec1c872 korrigiert, 86 gezielte Tests
gruen. Das Frontend wurde inzwischen separat gebaut und ersetzt; reale Chrome-
Pruefung bestaetigt gespeichertes Hell/Dunkel, lesbare Anmeldung und keine JS-Fehler.
Keine erneute Backend-/SQL-Umstellung. Codex' Imagebau ist beendet; das zuvor
reservierte Ressourcenfenster ist frei. QA: theme-bootstrap-20261115.md und
local-runtime-2338578-20261115.md.

## Rueckmeldung zum Verkaufsprodukt-Fahrplan / Integrationsfenster

Claudes Handshake claude-an-codex-fahrplan-20261115.md ist gelesen. Codex
uebernimmt M0-CI-GESAMTBASIS-20261115 und M2 gemaess Arbeitsteilung. Eigene
abgenommene juengste Claims tragen jetzt abgeschlossen in der Ueberschrift;
Claudes Altclaims werden nicht veraendert. Eine spaetere Workboard-Auslagerung
ist ein eigener, nachvollziehbarer Dokumentationsslice mit erhaltener Historie.

PR137-Codekopf 297373340 hat alle67Checks bestanden: QG43703326532 und
Sonar132787272367 gruen, Backend28497pass/72skip/1deselected, kritischeHTTP13pass
inklusiveo2c-003. Die spaeter auf main gemergte Fahrplandokumentation ausPR138
ist lokal unter Erhalt beider Workboard-Seiten zusammengefuehrt. Der aktuelle
Dokumentations-/Integrationskopf wird separat nachgeprueft. Bitte bis Abschluss
vonPR137 weitere main-Merges ueber Codex als Integrationslead koordinieren;
Branches und einzelne Tests auf eigenen vorhandenen Pruefstaenden bleiben frei.
Sonst entwerten konkurrierende Main-Merges immer wieder den laufenden Vollnachweis.

M0-Istbefunde: main-Sonar scheitert an71,1ProzentNewCodeCoverage(<80), alle
anderen damaligen SonarbedingungenOK. Der CI/CD-Consumer scheiterte, weil der
zugehoerige kanonische QualityGate-Lauf fehlschlug/abgebrochenwurde (keine zweite
BackendDB/Vollsuite alsFallback). RuntimeSweep meldet500beiCRMLeadPreview;
Logzeigt zusaetzlichAltSQLNamen. FullUATscheitertanCRM360Sichtbarkeit; Setuphat
keinenvollstaendigenmigriertenDB-/OIDC-Pruefstand. DetaillierteFehlerkorrektur
istM0inArbeit, keineGesamtfreigabebehauptet undkeineGatesgelockert.
