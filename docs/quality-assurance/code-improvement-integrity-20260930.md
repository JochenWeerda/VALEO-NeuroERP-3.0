---
title: Korrektheit und Dauerbetrieb des Code-Verbesserungszyklus
type: reference
audience: [agent, entwickler, qa, betrieb]
owner: Codex
status: aktiv
last_reviewed: 2026-09-30
description: Abfragebezogene Pagination, geschuetzte Baselines und einmalige CI-Evidenz.
---

# Code-Verbesserungszyklus

Prioritaet: Korrektheit, Widerspruchsfreiheit und Integration vor Laufkosten.
Die Fehleranalysen zu frischen Datenbanken, stillen Fallbacks, toten
Transaktionen, konkurrierenden Claims und widerspruechlichen Belegbindungen
bleiben fachliche Abnahmeregeln. Kein Scanner ersetzt ihre Vertragstests.

## Geschlossene technische Luecken

- `check_pagination.py` verfolgt Begrenzungen an Abfrageketten und lokalen
  Zuweisungen. Ein anderer Endpunkt, ein HTTP-Parameter oder ein Offset
  allein entwarnt keine `.all()`-Abfrage. Kommentare und Zeichenketten sind
  keine Aufrufe. Verzweigungen verlangen eine Grenze auf allen Wegen.
- Die genauere Erstinventur enthaelt **289 Abfragen in 262 Funktionen**.
  Dies ersetzt die methodisch unzureichende Zahl 53 Dateien; es ist kein
  Schuldenabbau. `config/pagination_baseline.json` ist funktionsbezogen;
  neue/gewachsene/verschobene Funde und nicht nachgezogener Abbau schlagen fehl.
- `check_baseline_integrity.py` vergleicht Godfile-, Geschaeftszeit-,
  Pagination- und Coverage-Baselines mit dem Ausgangscommit. Gemeinsam mit
  dem Code angehobene Schuld ist damit weiterhin rot. Eine neue Pagination-
  Erstbaseline darf nur den mit der neuen Methode gemessenen Altbestand des
  Ausgangscommits enthalten. Neue dateiweite Pagination-Ausnahmen sind verboten.
- Fehlende Coverage-Baselines und nicht synchronisierte Schwellwerte sind
  Fehler, keine Hinweise. Die Integritaetspruefung laeuft fuer jeden PR;
  ein Pfadfilter kann sie nicht bei reinen Script-/Config-Aenderungen umgehen.
- Der Quality Gate hat einen unabhaengigen Inventurjob und verbindliche
  Frontend-Unit-Tests. Zwei Worker begrenzen die Ressourcenlast; Testfristen
  bleiben unveraendert. Der Coverage-Provider ist exakt gesperrt, bestehende
  Paketaufloesungen wurden nicht aktualisiert.
- Sonar ist ein aufrufbarer Workflow desselben Quality-Gate-Runs: Backend-
  und Frontend-Coverage werden einmal erzeugt. Sidecars binden jeden Nachweis
  an Git-SHA und SHA256 des Dateiinhalts; fehlende/abweichende Artefakte sind
  Fehler. Migrationen und Tests werden dort nicht nochmals ausgefuehrt und
  nicht durch `|| true` unterdrueckt. Das Sonar-Qualitaetsgate wird abgewartet.
- Der bestehende Nightly erzeugt Metrik- und Verbesserungsartefakte lesend;
  kein direkter Commit/Push auf einen geschuetzten Branch.
- `run_improvement_pipelines.py` ersetzt den verwaisten linkup_mcp-Einstieg
  durch neun vorhandene Scanner, ohne neue Dienste oder optionale Pakete.
  Zwei begrenzte Worker, individuelle Timeouts und getrennte Ergebnisse
  verhindern Fehlerkaskaden. Rohlogs werden nicht in Artefakte kopiert.
  Veraendert sich der Arbeitsbaum waehrend der Messung, gilt der Lauf als rot.

## Betrieb

Lokal: `python scripts/run_improvement_pipelines.py --jobs 2 --timeout 120`.
Das Ergebnis steht in `artifacts/code-improvement.json`. Jeder Check nennt
Status, Exitcode, Laufzeit und Log-Hash; SHA und Arbeitsbaum-Hash identifizieren
den Stand. Scanner-Details lassen sich mit dem genannten Script direkt lesen.
Der Runner mutiert weder Fachdaten noch Baselines und ruft keine Netzwerkdienste.

Im PR prueft `path-guard` die Baseline gegen die PR-Basis. Der unabhaengige
Inventurjob erhebt die einzelnen Funde und publiziert auch bei Fehlern ein
Artefakt. Der taegliche vorhandene Nightly erhebt denselben Bestand erneut.
Ein neuer Befund wird als abgegrenzter Slice mit Owner, Fehlerursache,
Abnahmekriterien und Regressionstest bearbeitet; historische Nachweise bleiben
datierte Nachweise. Keine automatisch wiederholten fachlichen Testfehler.

## Lokale Nachweise und Grenzen

- 90 gezielte Tests fuer neue und bestehende Scanner-, Baseline-, Runner-,
  Workflow-, YAML- und Kompatibilitaetsvertraege bestanden.
- Neue Pagination-Ratsche und Baseline-Integritaet gegen Claim `c42ec7d34`
  lokal gruen; neue Erstbaseline ohne neue Schuld gegenueber dem Ausgangsstand.
- Frozen pnpm-Installation bestaetigt die Sperrdatei. Zwei fehlende lokale
  Cachepakete nachgeladen; Installationsskripte deaktiviert.
- Erster voller Frontend-Lauf: 913 bestanden, ein Import-Timeout unter hoher
  Parallelitaet (227 Sekunden). Wiederholung mit zwei Workern: **914/914 Tests
  in 212 Dateien bestanden**, Coverage erzeugt, 451 Sekunden. Die geringere
  Parallelitaet verbessert hier die Stabilitaet, nicht die gemessene Laufzeit;
  zukuenftige Laufzeitoptimierung muss diesen Korrektheitsnachweis erhalten.
- Der lokale Inventurbericht meldet laufende Fremdaenderungen korrekt rot:
  neues CRM-Godfile und Wachstum der Maskenbruecke; Snapshot wechselte im Lauf.
  Diese Fehler wurden weder durch Baseline-Anhebung noch durch Filter versteckt.

Externe Gates: erster realer GitHub-Lauf nach Integration, erforderliche Status-
Checks im Branchschutz, verfuegbarer Sonar-Token und Sonar-Projektkonfiguration.
Fork-PRs bekommen keine Sonar-Secrets; ihre verbindlichen Tests bleiben aktiv.
Keine produktive Datenbank wurde neu aufgebaut oder migriert.

## Fachlicher Restbestand

289 Scanner-Funde sind Verdachts-/Klassifikationsstellen, nicht 289 bestaetigte
Pagination-Bugs. Vollaggregate, technische Resultate und echte Entity-Listen
muessen je Funktion unterschieden werden. Bewiesene Vollaggregate bekommen
einen fachlichen Vertrag statt einer pauschalen dateiweiten Freistellung.
Unbekannte Abfragehelfer/rohe SQL-Grenzen werden konservativ nicht entwarnt.

Bestehende Domain-Handshakes zu Mandantentrennung, mutierenden Transaktionen,
fehlenden Migrationen und externen Freigaben bleiben offen, bis ihre konkrete
Wirkung samt Fehlerfaellen verifiziert ist. Die Architektur-Slices und aktiven
Claims bleiben beim jeweiligen Owner; eine gruene Bestandsratsche ist keine
Freigabe dieses Altbestands.
