---
title: Vor-Push-Pruefung ohne implizite Pruefstandwartung
type: reference
owner: Codex
status: in Arbeit
last_reviewed: 2026-11-23
---

# Ressourcenschutz vor dem Push

## Bestaetigter Befund

Die am19.11 integrierte Vor-Push-Kette konnte einen abweichenden valeo_probe
neu aufbauen und bei eigenen Migrationen hoch-/herunterstufen. Seed und
Rollen-/Eigentumsanpassungen gehoerten ebenfalls zum Standardlauf, auch bei
--ohne-tests. Ein eingebauter Zugangsdaten-Default ueberging fehlende explizite
Konfiguration. Fehlende Bereitschaft verhinderte nachfolgende Tests nicht.
Dies widersprach der verbindlichen gemeinsamen Ressourcenregel in AGENTS.md.

## Umsetzung

- Kein automatischer Reset, Upgrade, Downgrade, Seed oder Rechtewechsel.
- Ausdrueckliche PostgreSQL-Test-URL erforderlich; ungueltige/Entwicklungs-
  Verbindungen abweisen, keine Verbindungsdaten in Fehlermeldungen.
- Vergleichsstand und echte Konfliktmarker einschliesslich bereits committeter,
  vorgemerkter und lokaler Aenderungen vor Datenbankzugriff pruefen.
- Revision und ausgewaehlte App-Rolle/Schema-Rechte lesend pruefen, READ ONLY
  erzwingen und Verbindungspools auch bei Fehlern schliessen.
- Bei nicht bereitem Pruefstand vor Registern/Tests abbrechen; Wartung separat
  koordiniert. Ein erfolgreicher Check belegt den angegebenen Pruefumfang,
  nicht den vollstaendigen Seed-/ACL-Zustand einer CI-Datenbank.
- Tests weiter in Bloecken zu sechs Dateien. Statische Tabellenentfernungen
  beziehen betroffene Verbraucher und Schema-/RLS-Vertraege ein. Nicht
  auswertbares dynamisches DDL verlangt ausdruecklich --volle-tests. Dieser
  Modus prueft alle verfolgten Python-Testdateien in denselben Sechserbloecken
  nach unveraenderten Sicherheits-/Registerpruefungen und ohne DB-Wartung.
  Keine pauschale Wiederholung aller unveraenderten Tests je Migration.

## Nachweis

27 isolierte Regressionstests bestanden (ohne conftest/Plugin-Autoload und ohne
reale Datenbank). Abgedeckt: fehlende/ungueltige Konfiguration, Geheimnisschutz,
frueher Abbruch, normale und --ohne-tests-Ausfuehrung, echte Marker gegen
Code-Literale, S5-artige entfernte Tabellen, dynamisches DDL sowie READ ONLY
und Pool-Freigabe bei Erfolg/Fehler. Die bisherige Ressourcenregel gilt weiter.

Am23.11 meldet der Nutzer parallele Vor-Push-Laeufe von Claude fuer PR160/161.
Diese Umsetzung hat weder jene Worktrees noch deren Datenbankwartung oder
laufende Prozesse angefasst. Weitere reale DB-Abnahmen erst nach freiem Fenster.
GitHub-Abnahme und vollstaendige Integration stehen noch aus.
