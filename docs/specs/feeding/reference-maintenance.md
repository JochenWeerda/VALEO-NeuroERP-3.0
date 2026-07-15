---
title: "Fuetterungsberatung — Pflegevertrag des Architektur-Referenzwerks"
type: reference
audience: [architektur, entwickler, fachlich, qa, agent]
owner: domain/agrar
status: aktiv
last_reviewed: 2026-07-15
version: 1.0.0
description: Verbindliche Regeln, damit das 300–500-Seiten-Referenzwerk trotz Code-, OpenAPI- und Migrationsaenderungen eine verlaessliche Single Source of Truth bleibt.
---

# Pflegevertrag

## 1. Zweck

Das Referenzwerk soll Entscheidungen vorwegnehmen, ohne eine zweite technische
Wahrheit neben Code, Datenbank und generierter OpenAPI zu erzeugen. Es besteht aus
normativen Produktvertraegen, erklaerenden Architektursichten und generierten oder
quellengebundenen Inventaren.

## 2. Verbindlichkeitsklassen

| Klasse | Bedeutung | Beispiel | Konfliktregel |
|---|---|---|---|
| NORMATIV | fachliche oder architektonische Sollvorgabe | Statusautomat, Rollenmatrix, Invariante | Aenderung braucht Requirement-ID, Slice und Test |
| QUELLENGEBUNDEN | Abbild eines technischen Vertrags | Endpoint, Tabelle, Eventfeld | Code/OpenAPI/Migration ist Ausfuehrungsquelle; Doku-Drift muss im selben Slice korrigiert werden |
| ERKLAEREND | Begruendung, Beispiel, Lernpfad | Szenario, Begriffsbeispiel | darf normative Aussagen nicht erweitern |
| GEPLANT | noch nicht implementiertes Ziel | FEED-*-Arbeitspaket | muss Status und Abhaengigkeiten nennen |
| EXTERN BLOCKIERT | nicht repo-seitig lieferbar | DDW-Livevertrag | kein Mock darf als produktive Loesung gelten |

## 3. Quellenhierarchie

1. Fachliche Norm: freigegebene GfE-/DLG-Quelle und versionierter Golden-Test.
2. Produktanforderung: stabile `FEED-*`-ID im Lastenheft/Referenzwerk.
3. Architekturentscheidung: akzeptierter ADR und Domain Pack.
4. Laufzeitvertrag: Code, generierte OpenAPI, Alembic-Migration und Eventschema.
5. Bedienvertrag: ScreenDefinition/RenderPlan sowie Masken- und Workflowkatalog.
6. Planung: Workboard-Slice und Arbeitspaket.

Bei Widerspruch stoppt der umsetzende Slice, klassifiziert die Abweichung und
aktualisiert die hoeher priorisierte Quelle oder dokumentiert eine Migration.

## 4. Kapitelvertrag

Jedes Dokument 00–17 enthaelt:

- Owner, Status, Version und `last_reviewed`;
- normative IDs oder explizite Kennzeichnung als erklaerend;
- Quellen auf Code, ADR, OpenAPI, Migration oder Test;
- bekannte Abweichungen und naechste Arbeitspakete;
- keine erfundenen Endpunkte, Tabellen, Formeln oder Providerfaehigkeiten.

## 5. Aenderungsregeln je Artefakt

| Codeaenderung | Pflichtaktualisierung |
|---|---|
| neue/veraenderte Tabelle oder Index | 05 Datenmodell, Migrationsteil, Traceability, Tests |
| neuer/veraenderter Endpoint | 06 API, Domain Pack, OpenAPI-Beispiel, RBAC-Test |
| neue/veraenderte Maske | 07 Maskenkatalog, 10 UI/UX, Interaktions-/axe-Test |
| Status-/Prozesswechsel | 08 Workflow, 04 DDD, Event-/Audit-Test |
| neue Formel/Regel | 09 Regelwerk, Quellenreferenz, Golden-/Property-Test |
| neuer Agent oder Toolzugriff | 11 Agenten, Policy, Human-in-the-loop- und Halluzinationstest |
| neuer Connector | 12 Integrationen, Mapping, Quarantaene, Consent/Contract/Secret/Egress-Gates |
| neuer Slice | 17 Roadmap/Arbeitspaket, Workboard, Traceability |

## 6. Formel- und Regel-SSOT

Das Regelwerk beschreibt Eingaben, Einheiten, Gueltigkeit, Quellen, Randfaelle und
Testvektoren. Rechenformeln werden nur dann in Markdown ausgeschrieben, wenn sie
aus einer zitierbaren Norm stammen und exakt als Code-/Testreferenz verankert sind.
Die ausfuehrbare Wahrheit bleibt der versionierte Rechenkern plus Golden-Test.

## 7. API- und Datenmodell-SSOT

Der API-Katalog enthaelt fachliche Semantik und Beispiele. Feldlisten werden gegen
Pydantic/OpenAPI geprueft. Das Datenmodell enthaelt Zweck, Schluessel, Beziehungen,
Indizes, Tenant- und Historisierungsregeln; die physische Wahrheit bleibt Alembic.

## 8. Review- und Driftzyklus

- je Slice: betroffene Kapitel vor Abschluss aktualisieren;
- je Release: alle NORMATIV- und QUELLENGEBUNDEN-Kapitel reviewen;
- quartalsweise: externe Norm-/Providerquellen auf Version und Vertrag pruefen;
- Drift-Gate: tote Dateilinks, unbekannte Requirement-IDs, fehlende Testnachweise,
  Endpoint-/Tabellenabweichungen und veraltete `last_reviewed` blockieren;
- 300–500 Seiten sind Zielumfang, kein Qualitaetsmass: Duplikate werden entfernt,
  nicht durch Seitenzahl gerechtfertigt.

## 9. Status des Aufbaus

`FEED-SPEC-REFERENCE-038` baut die Kapitel in fachlich abhaengiger Reihenfolge auf:
Grundlagen -> DDD/Daten/API -> Masken/Workflows/Regeln -> Agenten/Integrationen/
Tests -> Migration/Rollout/Traceability/Roadmap. Jedes Kapitel wird erst als
`aktiv` markiert, wenn Quellen, IDs und mindestens ein Abnahmemechanismus vorhanden
sind; vorher bleibt es `in_arbeit`, nicht scheinbar abgeschlossen.
