---
title: Dependency- und Kompatibilitätspflege
type: reference
audience: [entwickler, betrieb]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-27
version: 3.0.0
description: Release-Kompatibilitätsmatrix, Toolchain-Pins, Dependency-Update-Prozess für VALEO NeuroERP.
---

# Dependency and Compatibility Maintenance

Stand: 2026-06-11

## Release-Kompatibilitaetsmatrix

Jede Release- oder Quality-Gate-Pruefung erzeugt ein gebundenes Artefakt:

- Generator: `scripts/generate_release_compatibility_matrix.py`
- Ausgabe: `artifacts/release-compatibility-matrix.json` und `.md`
- Kanonische Toolchain-Pins: `config/release-toolchain-pins.json`
- Drift-Check: `scripts/check_toolchain_pins.py`

Die Matrix enthaelt mindestens Git-SHA, App-Version, Alembic-Head,
API-Vertrag (`/api/v1`), Python/Node/pnpm-Versionen, Test-Toolchain-Pins
und optionale Backend-/Frontend-Image-Digests aus dem Release-Gate.

## Grundsatz

Eine Versionierung einzelner Module reicht nicht aus. Ein VALEO-Release
versioniert und prueft mindestens diese Vertraege gemeinsam:

1. Anwendung und interne Module
2. HTTP-API, Route-Parameter und erzeugte Clients
3. Datenbankschema, Migrationen und Bestandsdaten
4. Events, Queues und persistierte Nachrichten
5. Laufzeitplattform, Images und direkte/transitive Abhaengigkeiten

SemVer beschreibt die Absicht eines Herausgebers. Es beweist weder
Rueckwaertskompatibilitaet noch die Verwendbarkeit mit VALEO-Daten und
VALEO-Betriebsbedingungen.

## Erkenntnisse aus PROD-READINESS-001

- Parallele Migrationen erzeugten mehrere Alembic-Heads. Jeder Slice braucht
  deshalb einen Merge-Punkt; CI akzeptiert genau einen Head.
- Gestempelte Datenbanken konnten erwartete Spalten und Tabellen vermissen.
  Fresh-Install-Tests allein genuegen nicht; der Schema-Vertrag prueft
  repraesentative Tabellen und Spalten nach jeder Migration.
- Ein alter Governance-Vertrag erwartete `stock_movements`, waehrend das
  produktive Modell `inventory_stock_movements` verwendet. Vertragstests
  muessen kanonische Namen pruefen; tolerante Altpfade duerfen Drift nicht
  verdecken.
- Produzenten verwendeten einen Finanz-Kategoriewert, den der Validator nicht
  akzeptierte. Gemeinsame Enums und generierte Vertragstypen muessen die
  Quelle fuer API, Service und Datenbank sein.
- Ein LangGraph-Major aenderte den Saver-Vertrag zu einer expliziten
  SQLite-Verbindung. Compile-Erfolg ersetzt keine Laufzeit-Vertragstests.
- Feste Datumswerte alterten aus Dunning-Tests heraus. Zeitabhaengige Tests
  verwenden eine injizierte Uhr oder relative Testdaten.
- Implizite Event-Loops und globaler Cache-Zustand machten Tests
  reihenfolgeabhaengig. Tests muessen Zustand und Laufzeit explizit besitzen.
- Ein Demo-DSFinV-K-Export widersprach dem fail-closed Provider-Vertrag.
  Compliance-Pfade duerfen ohne reale Providerkonfiguration nicht erfolgreich
  simuliert werden.
- PowerShell-Glob-Verhalten wich von Bash ab. Release-Kommandos muessen auf
  dem Ziel-Runner und lokal mit portablen Argumenten geprueft werden.
- Parallele Volltests, Builds und Audits erschoepften unter Windows
  Datei-Handles (`EMFILE`) und erzeugten Scheinausfaelle. Schwere Gates laufen
  lokal seriell; CI trennt sie in isolierte Jobs mit eigenen Ressourcen.

## Verbindliche Kompatibilitaetsregeln

- Jede Release-Notiz enthaelt eine Matrix aus App-Version, Datenbankrevision,
  API-/Event-Vertrag, Node/Python-Version und Image-Digest.
- Datenbankaenderungen folgen Expand/Migrate/Contract. Destruktive Schritte
  erfolgen erst nach nachgewiesener Nutzung der neuen Struktur und einem
  getesteten Rollback- oder Forward-Fix-Pfad.
- CI prueft Fresh Install, Upgrade vom aeltesten unterstuetzten Stand, genau
  einen Alembic-Head und den erforderlichen Tabellen-/Spaltenvertrag.
- API- und Event-Aenderungen sind innerhalb des unterstuetzten Fensters
  additiv. Entfernen oder Umdeuten braucht eine neue Major-Version,
  Migrationshinweise und Verbraucher-Nachweis.
- Fachliche Literale werden nicht zwischen Modulen kopiert. Sie stammen aus
  einem kanonischen Vertrag und werden in TypeScript, Python und Datenbank
  validiert.
- Tests verwenden keine dauerhaft festen "aktuellen" Daten, keinen
  unbereinigten globalen Zustand und keine implizite externe Infrastruktur.
- Generierte Artefakte werden reproduzierbar gebaut und nicht unbeabsichtigt
  mit Quellaenderungen vermischt.

## Sicherheitsupdates

Bewertet werden CVSS, bekannte Ausnutzung, Produktions-Erreichbarkeit,
Datenklasse und vorhandene Kompensationsmassnahmen. Der hoechste relevante
Wert bestimmt die Prioritaet.

- `Critical` oder aktiv ausgenutzt: Release-Stop, Triage sofort, Ziel 24 Stunden.
- `High`: Release-Stop, Ziel 72 Stunden.
- `Moderate`: naechster geplanter Wartungsrelease, spaetestens 30 Tage.
- `Low`: gebuendelt, sofern keine fachliche Exposition die Einstufung erhoeht.

Eine Ausnahme ist nur zeitlich befristet zulaessig und dokumentiert CVE,
Owner, Erreichbarkeitsanalyse, Kompensationsmassnahme, Ablaufdatum und
Freigabe. Eine verwundbare Version wird nicht dauerhaft festgeschrieben.

## Vorgehen bei gefordertem Major-Update

1. Eigenen Security-Upgrade-Slice und ADR anlegen; keine Vermischung mit
   Fachfeatures.
2. Advisory, Changelog und Migrationsleitfaden lesen; betroffene direkte und
   transitive APIs sowie persistierte Formate inventarisieren.
3. Zielversion und Lockfile reproduzierbar fixieren, SBOM und Audit erneuern.
4. Compiler-, Contract-, Integrations-, Migrations-, Browser- und
   Negativtests erweitern, bevor die Anwendung angepasst wird.
5. Bei breiter API-Aenderung einen kleinen, zeitlich befristeten Adapter
   verwenden. Kein paralleler Dauerbetrieb zweier Bibliotheksgenerationen.
6. Datenmigration mit Produktionskopie oder repraesentativem Datenvolumen
   trocken pruefen; Backup und Restore nachweisen.
7. Staging und Canary gegen den unveraenderlichen Image-Digest ausrollen,
   Telemetrie und Fehlerraten beobachten.
8. Rollback nur bei kompatiblem Datenvertrag; sonst vorbereiteten Forward-Fix
   ausloesen.
9. Nach Stabilisierung Adapter und alte Vertragspfade entfernen und die
   Kompatibilitaetsmatrix aktualisieren.

Automatisierte Security-PRs sollen Patch/Minor regelmaessig gruppieren und
Security-Updates sofort oeffnen. Major-Upgrades werden mindestens monatlich in
einem Testzweig geprobt, damit der erste Kontakt nicht erst bei einer
kritischen Sicherheitsluecke erfolgt.

## AI-gestuetzte Major-Update-Arbeit

AI-Agenten duerfen Major Updates vorbereiten und implementieren, aber nicht
ohne reproduzierbaren Kompatibilitaetsnachweis abschliessen.

Pflicht fuer jeden AI-gestuetzten Security- oder Major-Update-Slice:

- Slice-YAML mit AI-Harness und `external_gates`.
- Advisory-Klassifikation: `fixable_minor`, `forced_major`,
  `accepted_temporary_risk`.
- Betroffene direkte und transitive Module.
- Liste der Contract-, Integration-, Migration-, Browser- und Negativtests.
- Canary-/Feature-Flag- oder Rollback-/Forward-Fix-Plan.
- Ablaufdatum und Owner fuer jede befristete Risikoakzeptanz.
- Aktualisierte Release-Kompatibilitaetsmatrix.

AI darf Changelogs, Migrationsleitfaeden und betroffene APIs zusammenfassen.
Die technische Entscheidung bleibt beim Owner des Security-Upgrade-Slices.
Bei POS, FiBu, Payroll, HR, DMS, QS, TSE, DATEV oder Datenschutz muss ein
externes oder simuliertes Pruefer-Gate im QA-Report stehen.

## Modell- und Tool-Kompatibilitaet

Die AI-Tool-Kompatibilitaetsmatrix liegt unter
`artifacts/ai-tool-compatibility-matrix.json`. Sie dokumentiert erlaubte
Werkzeuge, Datenklassen, Fallbacks und Restriktionen.

Verbindliche Regeln:

- Chat-only-Entscheidungen sind nicht releasefaehig; Vertraege, Prompts,
  Akzeptanzkriterien und Tests muessen ins Repo.
- Sensible Daten, Payroll, HR, personenbezogene Daten und Secrets duerfen nicht
  in externe Modelle gelangen. Es werden synthetische, anonymisierte oder lokale
  Kontexte genutzt.
- Ein Anbieter- oder Modellwechsel darf keine Architekturentscheidung loeschen;
  Slices muessen anhand von Workboard, Slice-YAML, Tests und Doku fortsetzbar
  sein.
- Lokale Modelle duerfen niedrigere Kosten oder bessere Datenresidenz liefern,
  aber keine niedrigeren Qualitaetsgates.

## Prueferevidenz

Fuer jede Freigabe werden Audit-Ausgaben, SBOM, Image-Digests,
Migrationsergebnis, Restore-Nachweis, Testreports, genehmigte Ausnahmen und
externe Freigaben unveraenderlich dem Commit-SHA zugeordnet. Simulierte
Prueferprofile sind Vorabnahmen und ersetzen keine reale Abnahme.
