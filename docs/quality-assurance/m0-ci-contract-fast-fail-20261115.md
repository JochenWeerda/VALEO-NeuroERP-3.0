---
title: M0 CI-Vertraege frueh und einmalig pruefen
owner: Codex
type: reference
status: in Arbeit
last_reviewed: 2026-11-15
---

# Fruehe CI-Vertragspruefung

## Befund und Korrektur

Quality Gate 43755370360 auf 249006062: 28395 bestanden, 71 uebersprungen,
einer abgewaehlt und genau ein Fehler nach 1948,01 Sekunden Vollsuite. Der Fehler
war ein veralteter Infrastrukturtest: Rollenvergabe wurde im selben Schritt wie
die erste Migration erwartet. Der inzwischen gepruefte Aufbau trennt dagegen
reines Migrationsschema, RLS-Export, additive ORM-Initialisierung mit Rollen,
physischen Anwendungskatalog und Verhaltenstests.

Der Vertrag prueft jetzt diese vollstaendige Reihenfolge, identische
DATABASE_URL/TEST_DATABASE_URL, den einzigen vorhandenen PostgreSQL-Pruefstand,
kanonische Rollenvergabe und Upload nur nach erfolgreichen strikten DB-Tests.
Kein --code-only beim physischen RLS-Nachweis, kein continue-on-error und kein
bedingtes Auslassen der DB-Verhaltenstests.

## Schnellere Ausfuehrung ohne Testverlust

Die beiden reinen Workflow-Testdateien test_consume_backend_evidence.py und
test_fsx003_quality_gate_wiring.py laufen vollstaendig im bestehenden,
datenbankfreien improvement-integrity-Job. Der Backendjob benoetigt jetzt sowohl
secret-scan als auch dieses bestandene Gate. Er wiederholt diese zwei Dateien
nicht; alle Produkt- und DB-Tests bleiben in der vollen Backend-Suite. Die
allgemeine pytest-Konfiguration wird nicht veraendert. FSX bleibt separat an
path-guard und verschwindet nicht hinter der Backend-Kaskade.

Eine neue Gegenpruefung verbindet die verpflichtende Abhaengigkeit, vollstaendige
fruehe Ausfuehrung und das Vermeiden der doppelten Ausfuehrung. Keine Coverage-
Quelle, Schwelle oder fachliche Testdatei wird ausgeschlossen. Keine neue
Datenbank, kein Container und kein neuer CI-Job.

## Nachweis

- 44 gezielte Workflow-/Provenance-Vertraege bestanden in 2,84 Sekunden.
- Der komplette neue fruehe Integritaets-Testsatz bestand lokal mit 135 Tests
  in 33,53 Sekunden, ohne conftest/App-Initialisierung oder Datenbankzugriff.
  Die beiden Testmengen ueberlappen und werden nicht addiert.
- Produktcode, Schemata und Konfiguration unter app/modules/packages/services/
  config/alembic sind gegen 249006062 unveraendert. Dessen echter StrictDB-Lauf
  43755370395 bestand mit 692 passed / 3 skipped einschliesslich der erweiterten
  Budget-Freigabegegenprobe. Die aktuelle Gesamt-CI muss den neuen Workflow
  weiterhin regulaer abnehmen; es wird kein Erfolgsnachweis aus einem roten Lauf
  freigeschaltet oder als gueltige Coverage ausgegeben.
