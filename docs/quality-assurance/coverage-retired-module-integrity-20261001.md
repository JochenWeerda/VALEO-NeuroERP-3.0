# Coverage-Ratsche: geloeschte Module und gueltige Messwerte

Stand 2026-10-01. Slice COVERAGE-RETIRED-MODULE-INTEGRITY-20261001,
Claim c3b1b7fa3. Antwort auf den Handshake KONTRAKT-EINE-ORDNUNG.

## Fehler und Vertrag

Die Up-Ratsche unterschied Modul-Loeschung nicht von einer gesenkten
Coverage-Schwelle. Vier bereits entfernte Kontraktmodule blieben deshalb
in Baseline und CRITICAL_THRESHOLDS. Ein passend gefuelltes Coverage-XML
konnte zudem eine noch aktive Schwelle ohne Quelldatei gruen erscheinen
lassen. Fuenf gezielte Vertraege scheiterten vor Reparatur, zehn bestanden:
artifacts/coverage-retired-before.log.

Ein Baselinepfad darf jetzt nur entfallen, wenn er im aufgeloesten Zielcommit
HEAD und im Arbeitsverzeichnis fehlt. Uncommittete Loeschung, untracked
Ersatzdatei, Symlink und nicht kanonische/aus app fuehrende Pfade sind kein
Loeschungsnachweis. NUL-getrennte Git-Inventare erhalten Unicode-Dateinamen.
Ein bereits verwaister Eintrag kann im spaeteren Cleanup entfallen.

Git-erkanntes Rename verlangt eine Nachfolgerschwelle mindestens auf alter
Hoehe. Bei Loeschung eines im Ausgangscommit vorhandenen Moduls zusammen
mit neuen Pythonmodulen ausserhalb tests werden keine unbelegten Annahmen getroffen:
alle neuen app-Module brauchen mindestens die entfallende Schwelle;
Nachfolger ausserhalb app verlangen einen eigenen Coverage-Vertrag. Das schuetzt
auch umgeschriebene Nachfolger unterhalb der Git-Rename-Aehnlichkeit.
Fachlich unabhaengige Neu- und Altmodule ggf. in getrennten nachvollziehbaren
Schritten bearbeiten. Reine Leichenbereinigung einer frueheren Loeschung
betrifft keine neue Code-Uebertragung.

Vorhandene Pfade bleiben unter der unveraenderten Up-Ratsche. Coverage prueft
zusaetzlich, dass jedes aktive Modul tatsaechlich existiert. Die vier verwaisten
Kontrakt-Schwellen wurden in Baseline und Checker gemeinsam entfernt:
kontrakt_actions, kontrakt_lifecycle_service, kontrakt_fixing_service und
kontrakt_settlement_service. Alle **99 lebenden Schwellen exakt unveraendert**;
ein vorhandener doppelter silo_target_cell-Schluessel mit identischem Wert
wurde bereinigt, ohne die wirksame Schwelle zu aendern.

Scope-Nachzug: NaN/Infinity konnten float-Vergleiche umgehen. Vier weitere
Messwertvertraege scheiterten, einer bestand vor Reparatur:
artifacts/coverage-measurement-before.log. Messungen, Baseline und aktive
Schwellwerte verlangen jetzt endliche numerische Werte zwischen null und eins;
keine booleschen oder String-Schwellwerte. Ungueltige Messwerte schlagen
verstaendlich fehl, statt einen Vergleich zu umgehen.

## Abnahme und Betrieb

Gemeinsamer finaler Lauf: **57 bestanden** (33,56 s), davon 30 neue
Retirement-/Coverage-Vertraege und 27 bestehende Baseline-/Workflow-/Pipeline-
Vertraege. artifacts/coverage-retired-final-tests.log. Echte temporaere Git-
Repositories beweisen Commit-Loeschung, alte Leichen, Rename-Transfer,
uncommittete Unicode-Loeschung, neue umgeschriebene Nachfolger und Ersatzdateien.
Coverage-Vertraege enthalten auch einen positiven Fall mit existierendem
Modul und erhaltener Schwelle. Keine Datenbank, kein Docker, kein Netzwerk.

Ruff, Whitespace und Baselineintegritaet gegen Claim gruen. Die numerische
Gleichheit der 99 verbleibenden Werte und genau vier entfallende Pfade wurde
gegen den Ausgangscommit separat bestaetigt. Der vorhandene Quality-Gate-
Workflow ruft beide Pruefungen weiterhin verbindlich auf; kein neuer Job
und keine Freistellung. Direktaufruf des Coverage-Scripts funktioniert weiter.

Der vorhandene lokale Coverage-Bericht bleibt rot: reale Unterschreitungen
und fehlende Messwerte, unter anderem portal_innendienst 31,5 % gegen 60 %,
external_gates 48,3 % gegen 70 %, quality_evidence 49,1 % gegen 70 %.
artifacts/critical-coverage-current.log. Das ist ein datierter Bericht, keine
neue Gesamtabdeckungsmessung. Die Gate-Reparatur ist keine behauptete
Coverage-Verbesserung. Frische SHA-/Run-gleiche CI-Evidence bleibt notwendig.

## Weitere offene Arbeit

Bankimport INT-BANK-001 hat weiterhin einen eigenen Parser-/Persistenz-/
Abgleichweg in bank_import.py und domain_finance. Der dortige Betrag-/
Substring-Fallback, float-Betraege, interne Commit-/Rollbackpfade und fehlende
Dateiwiederholung sind separate Integrationsbefunde; keine Bankroute wurde
in diesem Gate-Slice umgestellt. Zusammenspiel mit domain_erp und CAMT.08
braucht einen eigenen Architecture-/Finance-Claim und Abnahme.

GitHub-CI, frische Coverage und Deployment bleiben externe Abnahmen.
