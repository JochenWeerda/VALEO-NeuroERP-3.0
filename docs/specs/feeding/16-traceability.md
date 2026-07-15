---
title: "Fuetterungsberatung — Traceability- und Evidenzmodell"
type: specification
audience: [produkt, architektur, qa, audit, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
description: Durchgaengige Verknuepfung von Auftrag, Requirement, Architektur, Arbeitspaket, Code, Test, Migration und Betriebsnachweis.
---

# 16 — Traceability

## 1. Zweck

Traceability beweist nicht, dass irgendwo ein Test oder Dokument existiert. Sie
verbindet eine fachliche Aussage mit der aktuell ausgefuehrten Implementierung
und einem hinreichend starken Nachweis. Der aktuelle Requirementstatus steht in
`requirements-traceability.md`; dieses Kapitel definiert Struktur und Gates.

## 2. Identitaeten

| Artefakt | ID-Muster | Quelle |
|---|---|---|
| Requirement | `FEED-BUS-001`, `FEED-RAT-*` | Lastenheft/Traceability |
| normative Konzeptregel | `FEED-LH-*`, `FEED-FK-*` | Kapitel 02/03 |
| Akzeptanztest | `FEED-T001`–`FEED-T200` | Kapitel 13 |
| Arbeitspaket | `FEED-WP-001`–`FEED-WP-240` | Kapitel 17/work-packages |
| Umsetzungsslice | `FEED-CORE-015` usw. | Workboard/Slice-YAML |
| Migration/Event/API/Screen | stabiler technischer Name | Alembic/Schema/ScreenDefinition |

IDs werden nicht wiederverwendet. Umbenennung behaelt Alias und Historie.

## 3. Evidenzkette

```text
Auftrag/Quelle → Requirement → Fach-/Architekturregel → Arbeitspaket/Slice
→ Red-Test → Code/Migration/ScreenDefinition → Green/Regression
→ Traceabilitystatus → Release-/Betriebsnachweis
```

Ein Link auf einen breiten Testlauf ohne benannten Testfall beweist keine einzelne
Anforderung. Ein UI-Screenshot beweist keine serverseitige Autorisierung. Ein
Mock-Smoke beweist keinen Liveprovider.

## 4. Statusmodell

| Status | Erforderliche Evidenz |
|---|---|
| NOT_ANALYZED | noch keine belastbare Zuordnung |
| NOT_IMPLEMENTED | Ziel und Gap bekannt, kein produktiver Pfad |
| PARTIAL | benannter Teilpfad mit Test, Restgap explizit |
| IMPLEMENTED_UNVERIFIED | Code vorhanden, Abnahme unvollstaendig |
| VERIFIED | Requirement-spezifischer Code-, Test- und ggf. Betriebsnachweis |
| BLOCKED | externes Gate mit Owner und Wiederprueftermin |
| NOT_APPLICABLE | begruendete Produktentscheidung mit Review |

## 5. Pflichtfelder je VERIFIED-Zeile

- Requirement-ID und klare Anforderung;
- produktive Datei/API/Migration/ScreenDefinition;
- Testdatei und benannter Test oder stabile FEED-T-ID;
- verantwortlicher abgeschlossener Slice/Commit;
- Scope der Abnahme und bekannte Restgrenze;
- bei Livefunktion Umgebung, Zeitpunkt und Betriebsartefakt;
- bei Normregel Quelle und Regelversion.

## 6. TDD-Evidenz

Jeder produktive Slice fuehrt Test-ID, Red-Befehl/Fehler, Green-Lauf, relevante
Regression und Refactor-Notiz. Der Red-Nachweis darf lokal oder in einem separaten
Testcommit liegen; absichtlich rote Main-Pipelines sind nicht erforderlich.

## 7. Automatisierte Gates

Der Referenztest `tests/test_feeding_reference_catalog.py` prueft Kapitelvollstand,
240 eindeutige Pakete, Pflichtfelder und bekannte Test-IDs. Weitere Gates pruefen
Markdown/Governance, Agent-Handbuch, Screen-/commandEndpoint-Inventar, OpenAPI,
Alembic-Single-Head und Code-/Doku-Drift. Ein Gatefehler wird nicht durch Prosa
ueberschrieben, sondern behoben oder als benannte Altlast einem Paket zugeordnet.

## 8. Aenderungsfluss

1. Requirement und Test-ID bestimmen.
2. Arbeitspaket claimen; Abhaengigkeiten pruefen.
3. Red nachweisen, Green/Refactor/Regression liefern.
4. Kapitel 04–15 entsprechend der Aenderung aktualisieren.
5. `requirements-traceability.md` nur mit konkreter Evidenz hochstufen.
6. Workboard/Slice abschliessen und Release-Gates aktualisieren.

## 9. Audit und Aufbewahrung

Commit, CI-Lauf, Testartefakt, Migration und Go/No-Go-Entscheidung bleiben nach
Repository-/Betriebsrichtlinie erhalten. Personenbezogene oder betriebliche
Fachdaten werden nicht in Testlogs oder Dokumentation kopiert; Evidenz verwendet
synthetische IDs und technische Metadaten.

## 10. Review

QA ist Owner der Nachweisqualitaet, Domain/Produkt der fachlichen Aussage und
Architektur der Quellengrenzen. Vor jedem Release erfolgt eine
Requirement-fuer-Requirement-Pruefung; fehlende oder indirekte Evidenz gilt als
nicht erreicht.
