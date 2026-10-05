---
title: "ADR-048 Versionierte Futteranalyse mit Provenienz und bewusster Aktivierung"
type: adr
audience: [architektur, domain, entwickler, qa]
owner: domain/agrar
status: proposed
last_reviewed: 2026-07-15
version: 1.0.0
---

# ADR-048 Versionierte Futteranalyse mit Provenienz und bewusster Aktivierung

**Status:** Proposed

**Datum:** 2026-07-15

## Kontext

Der bestehende Grundfutteranalyse-Import speichert viele fachlich wertvolle
VDLUFA-Felder, kennt aber weder einen expliziten Feed-Bezug noch unveraenderliche
Revisionen, Original-/Rechenwert-Provenienz oder eine atomare aktive Version.
Ein zweites Analysemodell wuerde vorhandene Laborimporte und IDs duplizieren.

## Entscheidung

- `domain_shared.grundfutter_analysen` bleibt der Analyse-Kopf und wird additiv
  zum `FeedAnalysis`-Aggregat erweitert.
- Messwerte bewahren Originalwert und Originaleinheit; der kanonische
  Decimal-Rechenwert, Bezugsbasis, Methode und Wertstatus werden separat
  historisiert.
- Der serverseitige Lifecycle lautet `uploaded -> mapped -> draft -> validated
  -> released/superseded` beziehungsweise `rejected`. Abgeschlossene Versionen
  sind unveraenderlich.
- Pro Tenant, Feed und `scope_code` ist hoechstens eine released Analyse aktiv.
  Freigabe sperrt den Scope, ersetzt die vorige Version atomar und erzeugt fuer
  beide Analysen Auditrevisionen.
- PDF/CSV-Import ist zuerst eine nebenwirkungsfreie Vorschau. Bei importierten
  Dateien blockiert fehlende DMS-Belegreferenz die Freigabe; SHA-256 verbindet
  Vorschau, DMS-Objekt und Analyse.
- Fehlende Werte sind unbekannt und niemals Null. Schaetzungen tragen auf jedem
  Wert `value_status=estimated`.
- Die Legacy-Grundfutter-API bleibt les-/schreibkompatibel, kann Audit und
  Append-only-Verwerfen aber nicht mehr umgehen.
- Worklist und ObjectPage werden durch die zentrale Meridian-Runtime erzeugt;
  Import-, Validierungs- und Freigabedialoge bleiben schmale Domain-Overlays.

## Konsequenzen

Rationen koennen eine konkrete freigegebene Analyseversion referenzieren, ohne
dass eine neue Freigabe alte Rationsversionen veraendert. Laboradapter erhalten
einen stabilen Preview-/Provenienzvertrag. Ein produktiver DMS-Upload und
Virenscan bleiben Integrationsverantwortung; die Analyse-API akzeptiert nur die
revisionssichere Dokument-ID samt nachgewiesenem SHA-256.
